"""Tests for unit conversion."""

import pytest

from ductile_loads import ForceMoment, LoadCase, LoadSet, PointLoad, Units


# Conversion constants from the source
KLBS_TO_N = 4448.221628
KLBS_IN_TO_NM = 112.9848293


class TestConvertTo:
    def test_identity_conversion(self, simple_loadset):
        """N → N should produce identical values."""
        converted = simple_loadset.convert_to("N")
        orig_fx = simple_loadset.load_cases[0].point_loads[0].force_moment.fx
        conv_fx = converted.load_cases[0].point_loads[0].force_moment.fx
        assert conv_fx == pytest.approx(orig_fx)

    def test_n_to_kn(self, simple_loadset):
        converted = simple_loadset.convert_to("kN")
        assert converted.units.forces == "kN"
        assert converted.units.moments == "kNm"
        # fx=100 N → 0.1 kN
        fx = converted.load_cases[0].point_loads[0].force_moment.fx
        assert fx == pytest.approx(0.1)
        # mx=10 Nm → 0.01 kNm
        mx = converted.load_cases[0].point_loads[0].force_moment.mx
        assert mx == pytest.approx(0.01)

    def test_n_to_klbs(self, simple_loadset):
        converted = simple_loadset.convert_to("klbs")
        assert converted.units.forces == "klbs"
        assert converted.units.moments == "klbs.in"
        fx = converted.load_cases[0].point_loads[0].force_moment.fx
        assert fx == pytest.approx(100.0 / KLBS_TO_N)

    def test_kn_to_n(self, kn_loadset):
        converted = kn_loadset.convert_to("N")
        assert converted.units.forces == "N"
        assert converted.units.moments == "Nm"
        # 1 kN → 1000 N
        fx = converted.load_cases[0].point_loads[0].force_moment.fx
        assert fx == pytest.approx(1000.0)
        # 0.5 kNm → 500 Nm
        mx = converted.load_cases[0].point_loads[0].force_moment.mx
        assert mx == pytest.approx(500.0)

    def test_klbs_to_n(self):
        ls = LoadSet(
            name="klbs",
            version=1,
            units=Units(forces="klbs", moments="klbs.in"),
            load_cases=[
                LoadCase(
                    name="C",
                    point_loads=[
                        PointLoad(
                            name="P",
                            force_moment=ForceMoment(fx=1.0, mx=1.0),
                        ),
                    ],
                ),
            ],
        )
        converted = ls.convert_to("N")
        assert converted.load_cases[0].point_loads[0].force_moment.fx == pytest.approx(
            KLBS_TO_N
        )
        assert converted.load_cases[0].point_loads[0].force_moment.mx == pytest.approx(
            KLBS_IN_TO_NM
        )

    def test_chained_roundtrip(self, simple_loadset):
        """N → klbs → N should recover original values."""
        to_klbs = simple_loadset.convert_to("klbs")
        back_to_n = to_klbs.convert_to("N")
        for orig_lc, rt_lc in zip(
            simple_loadset.load_cases, back_to_n.load_cases, strict=True
        ):
            for orig_pl, rt_pl in zip(
                orig_lc.point_loads, rt_lc.point_loads, strict=True
            ):
                for attr in ("fx", "fy", "fz", "mx", "my", "mz"):
                    assert getattr(rt_pl.force_moment, attr) == pytest.approx(
                        getattr(orig_pl.force_moment, attr), rel=1e-9
                    )

    def test_n_kn_klbs_roundtrip(self, simple_loadset):
        """N → kN → klbs → N should recover original."""
        r = simple_loadset.convert_to("kN").convert_to("klbs").convert_to("N")
        orig_fx = simple_loadset.load_cases[0].point_loads[0].force_moment.fx
        rt_fx = r.load_cases[0].point_loads[0].force_moment.fx
        assert rt_fx == pytest.approx(orig_fx, rel=1e-9)

    def test_preserves_metadata(self, simple_loadset):
        converted = simple_loadset.convert_to("kN")
        assert converted.name == simple_loadset.name
        assert converted.description == simple_loadset.description
        assert converted.version == simple_loadset.version

    def test_negative_values_converted(self, simple_loadset):
        converted = simple_loadset.convert_to("kN")
        # fy=-50 N → -0.05 kN
        fy = converted.load_cases[0].point_loads[0].force_moment.fy
        assert fy == pytest.approx(-0.05)

    def test_zero_values_stay_zero(self, simple_loadset):
        converted = simple_loadset.convert_to("kN")
        # mz=0 should stay 0
        mz = converted.load_cases[0].point_loads[0].force_moment.mz
        assert mz == 0.0

    def test_moment_auto_pairing(self):
        """Force unit determines moment unit automatically."""
        ls = LoadSet(
            name="T",
            version=1,
            units=Units(forces="N", moments="Nm"),
            load_cases=[],
        )
        assert ls.convert_to("N").units.moments == "Nm"
        assert ls.convert_to("kN").units.moments == "kNm"
        assert ls.convert_to("klbs").units.moments == "klbs.in"


class TestImmutability:
    def test_convert_does_not_mutate_original(self, simple_loadset):
        orig_fx = simple_loadset.load_cases[0].point_loads[0].force_moment.fx
        simple_loadset.convert_to("kN")
        assert simple_loadset.load_cases[0].point_loads[0].force_moment.fx == orig_fx
        assert simple_loadset.units.forces == "N"
