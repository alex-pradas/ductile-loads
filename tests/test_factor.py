"""Tests for LoadSet.factor()."""

import pytest

from ductile_loads import LoadSet


class TestFactor:
    def test_factor_by_two(self, simple_loadset):
        scaled = simple_loadset.factor(by=2.0)
        orig_fx = simple_loadset.load_cases[0].point_loads[0].force_moment.fx
        assert scaled.load_cases[0].point_loads[0].force_moment.fx == pytest.approx(
            orig_fx * 2.0
        )

    def test_factor_by_zero(self, simple_loadset):
        scaled = simple_loadset.factor(by=0.0)
        for lc in scaled.load_cases:
            for pl in lc.point_loads:
                for attr in ("fx", "fy", "fz", "mx", "my", "mz"):
                    assert getattr(pl.force_moment, attr) == 0.0

    def test_factor_by_negative_one(self, simple_loadset):
        scaled = simple_loadset.factor(by=-1.0)
        for orig_lc, scaled_lc in zip(
            simple_loadset.load_cases, scaled.load_cases, strict=True
        ):
            for orig_pl, scaled_pl in zip(
                orig_lc.point_loads, scaled_lc.point_loads, strict=True
            ):
                for attr in ("fx", "fy", "fz", "mx", "my", "mz"):
                    assert getattr(scaled_pl.force_moment, attr) == pytest.approx(
                        -getattr(orig_pl.force_moment, attr)
                    )

    def test_factor_by_fractional(self, simple_loadset):
        scaled = simple_loadset.factor(by=0.5)
        orig_fx = simple_loadset.load_cases[0].point_loads[0].force_moment.fx
        assert scaled.load_cases[0].point_loads[0].force_moment.fx == pytest.approx(
            orig_fx * 0.5
        )

    def test_factor_preserves_metadata(self, simple_loadset):
        scaled = simple_loadset.factor(by=1.5)
        assert scaled.name == simple_loadset.name
        assert scaled.version == simple_loadset.version
        assert scaled.units.forces == simple_loadset.units.forces
        assert scaled.units.moments == simple_loadset.units.moments

    def test_factor_preserves_structure(self, simple_loadset):
        scaled = simple_loadset.factor(by=3.0)
        assert len(scaled.load_cases) == len(simple_loadset.load_cases)
        for orig_lc, s_lc in zip(
            simple_loadset.load_cases, scaled.load_cases, strict=True
        ):
            assert s_lc.name == orig_lc.name
            assert len(s_lc.point_loads) == len(orig_lc.point_loads)

    def test_factor_does_not_mutate_original(self, simple_loadset):
        orig_fx = simple_loadset.load_cases[0].point_loads[0].force_moment.fx
        simple_loadset.factor(by=10.0)
        assert simple_loadset.load_cases[0].point_loads[0].force_moment.fx == orig_fx

    def test_factor_by_one_is_identity(self, simple_loadset):
        scaled = simple_loadset.factor(by=1.0)
        for orig_lc, s_lc in zip(
            simple_loadset.load_cases, scaled.load_cases, strict=True
        ):
            for orig_pl, s_pl in zip(
                orig_lc.point_loads, s_lc.point_loads, strict=True
            ):
                for attr in ("fx", "fy", "fz", "mx", "my", "mz"):
                    assert getattr(s_pl.force_moment, attr) == pytest.approx(
                        getattr(orig_pl.force_moment, attr)
                    )
