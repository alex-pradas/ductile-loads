"""Tests for envelope() and get_point_extremes()."""

import json
from pathlib import Path

import pytest

from ductile_loads import ForceMoment, LoadCase, LoadSet, PointLoad, Units


class TestGetPointExtremes:
    def test_returns_correct_structure(self, simple_loadset):
        extremes = simple_loadset.get_point_extremes()
        assert "PointA" in extremes
        assert "PointB" in extremes
        assert "max" in extremes["PointA"]["fx"]
        assert "min" in extremes["PointA"]["fx"]

    def test_max_values(self, simple_loadset):
        extremes = simple_loadset.get_point_extremes()
        # PointA fx: Case_A=100, Case_B=500 → max is 500 from Case_B
        assert extremes["PointA"]["fx"]["max"]["value"] == pytest.approx(500.0)
        assert extremes["PointA"]["fx"]["max"]["loadcase"] == "Case_B"

    def test_min_values(self, simple_loadset):
        extremes = simple_loadset.get_point_extremes()
        # PointA fy: Case_A=-50, Case_B=200 → min is -50 from Case_A
        assert extremes["PointA"]["fy"]["min"]["value"] == pytest.approx(-50.0)
        assert extremes["PointA"]["fy"]["min"]["loadcase"] == "Case_A"

    def test_zero_components_filtered(self):
        """Components where both max and min are 0 should be excluded."""
        ls = LoadSet(
            name="Zero",
            version=1,
            units=Units(),
            load_cases=[
                LoadCase(
                    name="C",
                    point_loads=[
                        PointLoad(name="P", force_moment=ForceMoment(fx=10.0)),
                    ],
                ),
            ],
        )
        extremes = ls.get_point_extremes()
        # Only fx should be present (all others are 0.0 in both cases)
        assert "fx" in extremes["P"]
        assert "fy" not in extremes["P"]
        assert "mz" not in extremes["P"]

    def test_all_zero_point_excluded(self):
        """Points with only zero components should not appear."""
        ls = LoadSet(
            name="AllZero",
            version=1,
            units=Units(),
            load_cases=[
                LoadCase(
                    name="C",
                    point_loads=[
                        PointLoad(name="P", force_moment=ForceMoment()),
                    ],
                ),
            ],
        )
        extremes = ls.get_point_extremes()
        assert extremes == {}

    def test_writes_output_file(self, simple_loadset, tmp_path):
        out = tmp_path / "extremes.json"
        extremes = simple_loadset.get_point_extremes(output=out)
        assert out.exists()
        loaded = json.loads(out.read_text())
        assert loaded == extremes

    def test_single_loadcase(self):
        """With one load case, max and min are the same value."""
        ls = LoadSet(
            name="Single",
            version=1,
            units=Units(),
            load_cases=[
                LoadCase(
                    name="Only",
                    point_loads=[
                        PointLoad(name="P", force_moment=ForceMoment(fx=42.0)),
                    ],
                ),
            ],
        )
        extremes = ls.get_point_extremes()
        assert extremes["P"]["fx"]["max"]["value"] == 42.0
        assert extremes["P"]["fx"]["min"]["value"] == 42.0


class TestEnvelope:
    def test_reduces_load_cases(self, multi_case_loadset):
        env = multi_case_loadset.envelope()
        # Case_Neutral has no extremes, so it should be dropped
        names = [lc.name for lc in env.load_cases]
        assert "Case_Neutral" not in names

    def test_includes_max_cases(self, multi_case_loadset):
        env = multi_case_loadset.envelope()
        names = [lc.name for lc in env.load_cases]
        assert "Case_Max_FX" in names  # fx=1000 is global max
        assert "Case_Max_FZ" in names  # fz=600 is global max
        assert "Case_Mixed" in names  # mx=50 is global max

    def test_includes_negative_min(self, multi_case_loadset):
        env = multi_case_loadset.envelope()
        names = [lc.name for lc in env.load_cases]
        # Case_Min_FY has fy=-800, which is negative → included
        assert "Case_Min_FY" in names

    def test_excludes_non_negative_min(self):
        """Min values ≥ 0 should NOT cause inclusion."""
        ls = LoadSet(
            name="T",
            version=1,
            units=Units(),
            load_cases=[
                LoadCase(
                    name="High",
                    point_loads=[
                        PointLoad(name="P", force_moment=ForceMoment(fx=100.0)),
                    ],
                ),
                LoadCase(
                    name="Low",
                    point_loads=[
                        PointLoad(name="P", force_moment=ForceMoment(fx=10.0)),
                    ],
                ),
            ],
        )
        env = ls.envelope()
        names = [lc.name for lc in env.load_cases]
        # "High" has global max fx=100 → included
        assert "High" in names
        # "Low" has min fx=10 which is positive → NOT included via min rule
        # But "Low" might still be excluded since its min is not negative
        assert len(env.load_cases) == 1

    def test_deduplication(self):
        """A case holding multiple extremes should appear only once."""
        ls = LoadSet(
            name="T",
            version=1,
            units=Units(),
            load_cases=[
                LoadCase(
                    name="MaxAll",
                    point_loads=[
                        PointLoad(
                            name="P",
                            force_moment=ForceMoment(fx=100.0, fy=200.0),
                        ),
                    ],
                ),
            ],
        )
        env = ls.envelope()
        assert len(env.load_cases) == 1

    def test_empty_loadset_raises(self, empty_loadset):
        with pytest.raises(ValueError, match="empty"):
            empty_loadset.envelope()

    def test_preserves_metadata(self, multi_case_loadset):
        env = multi_case_loadset.envelope()
        assert env.name == multi_case_loadset.name
        assert env.version == multi_case_loadset.version
        assert env.units.forces == multi_case_loadset.units.forces

    def test_preserves_point_data(self, multi_case_loadset):
        """Envelope should not modify point load values."""
        env = multi_case_loadset.envelope()
        max_fx_case = next(lc for lc in env.load_cases if lc.name == "Case_Max_FX")
        assert max_fx_case.point_loads[0].force_moment.fx == pytest.approx(1000.0)

    def test_does_not_mutate_original(self, multi_case_loadset):
        orig_count = len(multi_case_loadset.load_cases)
        multi_case_loadset.envelope()
        assert len(multi_case_loadset.load_cases) == orig_count

    def test_preserves_order(self, multi_case_loadset):
        """Envelope cases should maintain their original order."""
        env = multi_case_loadset.envelope()
        names = [lc.name for lc in env.load_cases]
        # Original order: Max_FX, Min_FY, Max_FZ, Mixed, Neutral
        # Envelope should keep order without Neutral
        for i in range(len(names) - 1):
            orig_idx_a = next(
                j
                for j, lc in enumerate(multi_case_loadset.load_cases)
                if lc.name == names[i]
            )
            orig_idx_b = next(
                j
                for j, lc in enumerate(multi_case_loadset.load_cases)
                if lc.name == names[i + 1]
            )
            assert orig_idx_a < orig_idx_b
