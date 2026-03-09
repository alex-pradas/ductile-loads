"""Tests for compare_to(), LoadSetCompare, and new_exceeds_old()."""

import json

import pytest

from ductile_loads import (
    ComparisonRow,
    ForceMoment,
    LoadCase,
    LoadSet,
    LoadSetCompare,
    PointLoad,
    Units,
)


def _make_loadset(name, version, forces, moments, cases):
    """Helper to quickly build a LoadSet from (case_name, point_name, fm_kwargs) tuples."""
    load_cases = []
    for case_name, points in cases:
        point_loads = [
            PointLoad(name=pn, force_moment=ForceMoment(**kw)) for pn, kw in points
        ]
        load_cases.append(LoadCase(name=case_name, point_loads=point_loads))
    return LoadSet(
        name=name,
        version=version,
        units=Units(forces=forces, moments=moments),
        load_cases=load_cases,
    )


class TestCompareTo:
    def test_basic_comparison(self, simple_loadset):
        other = simple_loadset.factor(by=1.1)
        cmp = simple_loadset.compare_to(other)
        assert isinstance(cmp, LoadSetCompare)
        assert len(cmp.comparison_rows) > 0

    def test_metadata_preserved(self, simple_loadset):
        other = simple_loadset.factor(by=1.0)
        cmp = simple_loadset.compare_to(other)
        assert cmp.loadset1_metadata["name"] == "Simple"
        assert cmp.loadset2_metadata["name"] == "Simple"
        assert cmp.loadset1_metadata["version"] == 1

    def test_identical_sets_zero_diff(self, simple_loadset):
        cmp = simple_loadset.compare_to(simple_loadset)
        for row in cmp.comparison_rows:
            assert row.abs_diff == pytest.approx(0.0)
            assert row.pct_diff == pytest.approx(0.0)

    def test_abs_diff_calculation(self):
        ls1 = _make_loadset(
            "A", 1, "N", "Nm", [("C", [("P", {"fx": 100.0})])]
        )
        ls2 = _make_loadset(
            "B", 1, "N", "Nm", [("C", [("P", {"fx": 150.0})])]
        )
        cmp = ls1.compare_to(ls2)
        max_row = next(
            r for r in cmp.comparison_rows
            if r.component == "fx" and r.type == "max"
        )
        assert max_row.loadset1_value == pytest.approx(100.0)
        assert max_row.loadset2_value == pytest.approx(150.0)
        assert max_row.abs_diff == pytest.approx(50.0)

    def test_pct_diff_calculation(self):
        ls1 = _make_loadset(
            "A", 1, "N", "Nm", [("C", [("P", {"fx": 200.0})])]
        )
        ls2 = _make_loadset(
            "B", 1, "N", "Nm", [("C", [("P", {"fx": 250.0})])]
        )
        cmp = ls1.compare_to(ls2)
        max_row = next(
            r for r in cmp.comparison_rows
            if r.component == "fx" and r.type == "max"
        )
        # pct_diff = (|250 - 200| / |200|) * 100 = 25%
        assert max_row.pct_diff == pytest.approx(25.0)

    def test_zero_base_gives_inf_pct(self):
        ls1 = _make_loadset(
            "A", 1, "N", "Nm", [("C", [("P", {"fx": 0.0, "fy": 10.0})])]
        )
        ls2 = _make_loadset(
            "B", 1, "N", "Nm", [("C", [("P", {"fx": 50.0, "fy": 10.0})])]
        )
        cmp = ls1.compare_to(ls2)
        fx_max = next(
            r for r in cmp.comparison_rows
            if r.component == "fx" and r.type == "max"
        )
        assert fx_max.pct_diff == float("inf")

    def test_auto_unit_conversion(self):
        ls_n = _make_loadset(
            "N_Set", 1, "N", "Nm", [("C", [("P", {"fx": 1000.0})])]
        )
        ls_kn = _make_loadset(
            "KN_Set", 1, "kN", "kNm", [("C", [("P", {"fx": 1.0})])]
        )
        cmp = ls_n.compare_to(ls_kn)
        fx_max = next(
            r for r in cmp.comparison_rows
            if r.component == "fx" and r.type == "max"
        )
        # Both should be 1000 N after conversion
        assert fx_max.abs_diff == pytest.approx(0.0, abs=1e-6)

    def test_not_a_loadset_raises(self, simple_loadset):
        with pytest.raises(ValueError, match="LoadSet"):
            simple_loadset.compare_to("not a loadset")

    def test_disjoint_points(self):
        """Points in only one set should still appear in comparison."""
        ls1 = _make_loadset(
            "A", 1, "N", "Nm", [("C", [("P1", {"fx": 100.0})])]
        )
        ls2 = _make_loadset(
            "B", 1, "N", "Nm", [("C", [("P2", {"fx": 200.0})])]
        )
        cmp = ls1.compare_to(ls2)
        point_names = {r.point_name for r in cmp.comparison_rows}
        assert "P1" in point_names
        assert "P2" in point_names

    def test_does_not_mutate_original(self, simple_loadset):
        other = simple_loadset.factor(by=2.0)
        orig_fx = simple_loadset.load_cases[0].point_loads[0].force_moment.fx
        simple_loadset.compare_to(other)
        assert simple_loadset.load_cases[0].point_loads[0].force_moment.fx == orig_fx


class TestNewExceedsOld:
    def test_scaled_up_exceeds(self, simple_loadset):
        bigger = simple_loadset.factor(by=1.5)
        cmp = simple_loadset.compare_to(bigger)
        assert cmp.new_exceeds_old() is True

    def test_within_range_does_not_exceed(self):
        """New set with tighter envelope should not exceed old."""
        ls_wide = _make_loadset(
            "Wide", 1, "N", "Nm",
            [
                ("C1", [("P", {"fx": 200.0, "fy": -100.0})]),
                ("C2", [("P", {"fx": -200.0, "fy": 100.0})]),
            ],
        )
        ls_narrow = _make_loadset(
            "Narrow", 1, "N", "Nm",
            [
                ("C1", [("P", {"fx": 150.0, "fy": -50.0})]),
                ("C2", [("P", {"fx": -150.0, "fy": 50.0})]),
            ],
        )
        cmp = ls_wide.compare_to(ls_narrow)
        assert cmp.new_exceeds_old() is False

    def test_identical_does_not_exceed(self, simple_loadset):
        cmp = simple_loadset.compare_to(simple_loadset)
        assert cmp.new_exceeds_old() is False

    def test_empty_rows_returns_false(self):
        cmp = LoadSetCompare(
            loadset1_metadata={},
            loadset2_metadata={},
            comparison_rows=[],
        )
        assert cmp.new_exceeds_old() is False

    def test_exceeds_on_min_side(self):
        """More negative min in new set → exceeds."""
        ls1 = _make_loadset(
            "A", 1, "N", "Nm",
            [("C1", [("P", {"fx": 100.0})]), ("C2", [("P", {"fx": -50.0})])],
        )
        ls2 = _make_loadset(
            "B", 1, "N", "Nm",
            [("C1", [("P", {"fx": 80.0})]), ("C2", [("P", {"fx": -100.0})])],
        )
        cmp = ls1.compare_to(ls2)
        # max: 100 vs 80 → no exceed. min: -50 vs -100 → exceeds (more negative)
        assert cmp.new_exceeds_old() is True

    def test_does_not_exceed_when_within_range(self):
        ls1 = _make_loadset(
            "A", 1, "N", "Nm",
            [("C1", [("P", {"fx": 100.0})]), ("C2", [("P", {"fx": -50.0})])],
        )
        ls2 = _make_loadset(
            "B", 1, "N", "Nm",
            [("C1", [("P", {"fx": 80.0})]), ("C2", [("P", {"fx": -30.0})])],
        )
        cmp = ls1.compare_to(ls2)
        assert cmp.new_exceeds_old() is False


class TestLoadSetCompareIO:
    def test_to_dict_structure(self, simple_loadset):
        cmp = simple_loadset.compare_to(simple_loadset)
        d = cmp.to_dict()
        assert "report_metadata" in d
        assert "comparisons" in d
        assert "loadcases_info" in d["report_metadata"]
        assert "loadset1" in d["report_metadata"]["loadcases_info"]
        assert "loadset2" in d["report_metadata"]["loadcases_info"]

    def test_to_json_valid(self, simple_loadset):
        cmp = simple_loadset.compare_to(simple_loadset)
        j = cmp.to_json()
        data = json.loads(j)
        assert "comparisons" in data

    def test_to_json_indent(self, simple_loadset):
        cmp = simple_loadset.compare_to(simple_loadset)
        j = cmp.to_json(indent=4)
        assert "    " in j

    def test_to_dict_row_count(self, simple_loadset):
        cmp = simple_loadset.compare_to(simple_loadset)
        d = cmp.to_dict()
        assert len(d["comparisons"]) == len(cmp.comparison_rows)
