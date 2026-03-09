"""Tests for Pydantic data model construction and validation."""

import pytest
from pydantic import ValidationError

from ductile_loads import (
    ComparisonRow,
    ForceMoment,
    LoadCase,
    LoadSet,
    PointLoad,
    Units,
)


class TestForceMoment:
    def test_defaults_all_zero(self):
        fm = ForceMoment()
        for attr in ("fx", "fy", "fz", "mx", "my", "mz"):
            assert getattr(fm, attr) == 0.0

    def test_explicit_values(self):
        fm = ForceMoment(fx=1.0, fy=2.0, fz=3.0, mx=4.0, my=5.0, mz=6.0)
        assert fm.fx == 1.0
        assert fm.mz == 6.0

    def test_partial_values(self):
        fm = ForceMoment(fx=42.0)
        assert fm.fx == 42.0
        assert fm.fy == 0.0

    def test_negative_values(self):
        fm = ForceMoment(fx=-100.0, my=-200.0)
        assert fm.fx == -100.0
        assert fm.my == -200.0

    def test_rejects_string(self):
        with pytest.raises(ValidationError):
            ForceMoment(fx="not_a_number")


class TestPointLoad:
    def test_construction(self):
        pl = PointLoad(name="P1", force_moment=ForceMoment(fx=10.0))
        assert pl.name == "P1"
        assert pl.force_moment.fx == 10.0

    def test_name_optional(self):
        pl = PointLoad(force_moment=ForceMoment())
        assert pl.name is None

    def test_force_moment_required(self):
        with pytest.raises(ValidationError):
            PointLoad(name="P1")


class TestLoadCase:
    def test_defaults(self):
        lc = LoadCase()
        assert lc.name is None
        assert lc.description is None
        assert lc.point_loads == []

    def test_with_point_loads(self):
        lc = LoadCase(
            name="LC1",
            point_loads=[PointLoad(name="P", force_moment=ForceMoment())],
        )
        assert len(lc.point_loads) == 1


class TestUnits:
    def test_defaults(self):
        u = Units()
        assert u.forces == "N"
        assert u.moments == "Nm"

    def test_valid_combinations(self):
        for f, m in [("N", "Nm"), ("kN", "kNm"), ("klbs", "klbs.in"), ("N", "Nmm")]:
            u = Units(forces=f, moments=m)
            assert u.forces == f
            assert u.moments == m

    def test_invalid_force_unit(self):
        with pytest.raises(ValidationError):
            Units(forces="lbs")

    def test_invalid_moment_unit(self):
        with pytest.raises(ValidationError):
            Units(moments="ft.lbs")


class TestLoadSet:
    def test_minimal_construction(self):
        ls = LoadSet(name=None, version=1, units=Units(), load_cases=[])
        assert ls.name is None
        assert ls.loads_type is None

    def test_full_construction(self, simple_loadset):
        assert simple_loadset.name == "Simple"
        assert simple_loadset.version == 1
        assert len(simple_loadset.load_cases) == 2
        assert simple_loadset.loads_type == "limit"

    def test_loads_type_validation(self):
        with pytest.raises(ValidationError):
            LoadSet(
                name="Bad",
                version=1,
                units=Units(),
                load_cases=[],
                loads_type="invalid",
            )

    def test_version_required(self):
        with pytest.raises(ValidationError):
            LoadSet(name="NoVer", units=Units(), load_cases=[])


class TestComparisonRow:
    def test_construction(self):
        row = ComparisonRow(
            point_name="P1",
            component="fx",
            type="max",
            loadset1_value=100.0,
            loadset2_value=120.0,
            loadset1_loadcase="CaseA",
            loadset2_loadcase="CaseB",
            abs_diff=20.0,
            pct_diff=20.0,
        )
        assert row.point_name == "P1"
        assert row.abs_diff == 20.0

    def test_invalid_component(self):
        with pytest.raises(ValidationError):
            ComparisonRow(
                point_name="P1",
                component="fq",
                type="max",
                loadset1_value=0.0,
                loadset2_value=0.0,
                loadset1_loadcase="A",
                loadset2_loadcase="B",
                abs_diff=0.0,
                pct_diff=0.0,
            )

    def test_invalid_type(self):
        with pytest.raises(ValidationError):
            ComparisonRow(
                point_name="P1",
                component="fx",
                type="avg",
                loadset1_value=0.0,
                loadset2_value=0.0,
                loadset1_loadcase="A",
                loadset2_loadcase="B",
                abs_diff=0.0,
                pct_diff=0.0,
            )
