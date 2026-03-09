from pathlib import Path

import pytest

from ductile_loads import (
    ForceMoment,
    LoadCase,
    LoadSet,
    PointLoad,
    Units,
)

SAMPLE_DATA = Path(__file__).parent / "sample_data"


@pytest.fixture
def simple_loadset() -> LoadSet:
    """Two load cases, two points, known deterministic values."""
    return LoadSet(
        name="Simple",
        description="Fixture",
        version=1,
        units=Units(forces="N", moments="Nm"),
        loads_type="limit",
        load_cases=[
            LoadCase(
                name="Case_A",
                point_loads=[
                    PointLoad(
                        name="PointA",
                        force_moment=ForceMoment(
                            fx=100.0, fy=-50.0, fz=200.0, mx=10.0, my=-20.0
                        ),
                    ),
                    PointLoad(
                        name="PointB",
                        force_moment=ForceMoment(
                            fx=-300.0, fy=150.0, my=30.0, mz=-15.0
                        ),
                    ),
                ],
            ),
            LoadCase(
                name="Case_B",
                point_loads=[
                    PointLoad(
                        name="PointA",
                        force_moment=ForceMoment(
                            fx=500.0, fy=200.0, fz=-100.0, mx=-5.0, my=40.0, mz=25.0
                        ),
                    ),
                    PointLoad(
                        name="PointB",
                        force_moment=ForceMoment(
                            fx=50.0, fy=-400.0, fz=75.0, mx=60.0, my=-10.0
                        ),
                    ),
                ],
            ),
        ],
    )


@pytest.fixture
def multi_case_loadset() -> LoadSet:
    """Five load cases with values designed for predictable envelope selection.

    Envelope should pick:
      - Case_Max_FX (fx=1000 is the global max for PointA fx)
      - Case_Min_FY (fy=-800 is the global min for PointA fy, negative → included)
      - Case_Max_FZ (fz=600, global max for PointA fz)
      - Case_Mixed  (mx=50 is the global max for PointA mx)
      - Case_Neutral should be dropped (no extremes)
    """
    def _pl(fx=0.0, fy=0.0, fz=0.0, mx=0.0, my=0.0, mz=0.0):
        return PointLoad(
            name="PointA",
            force_moment=ForceMoment(fx=fx, fy=fy, fz=fz, mx=mx, my=my, mz=mz),
        )

    return LoadSet(
        name="MultiCase",
        version=2,
        units=Units(forces="N", moments="Nm"),
        load_cases=[
            LoadCase(name="Case_Max_FX", point_loads=[_pl(fx=1000.0, fy=10.0)]),
            LoadCase(name="Case_Min_FY", point_loads=[_pl(fy=-800.0)]),
            LoadCase(name="Case_Max_FZ", point_loads=[_pl(fz=600.0)]),
            LoadCase(name="Case_Mixed", point_loads=[_pl(fx=100.0, mx=50.0)]),
            LoadCase(name="Case_Neutral", point_loads=[_pl(fx=50.0, fy=5.0)]),
        ],
    )


@pytest.fixture
def kn_loadset() -> LoadSet:
    """A LoadSet in kN/kNm for cross-unit testing."""
    return LoadSet(
        name="KN_Set",
        version=1,
        units=Units(forces="kN", moments="kNm"),
        load_cases=[
            LoadCase(
                name="KN_Case",
                point_loads=[
                    PointLoad(
                        name="PointA",
                        force_moment=ForceMoment(fx=1.0, fy=-2.0, mx=0.5),
                    ),
                ],
            ),
        ],
    )


@pytest.fixture
def empty_loadset() -> LoadSet:
    """A LoadSet with no load cases."""
    return LoadSet(
        name="Empty",
        version=1,
        units=Units(),
        load_cases=[],
    )


@pytest.fixture
def sample_json_path() -> Path:
    return SAMPLE_DATA / "simple_loadset.json"


@pytest.fixture
def sample_ansys_path() -> Path:
    return SAMPLE_DATA / "simple_ansys.inp"


@pytest.fixture
def malformed_ansys_path() -> Path:
    return SAMPLE_DATA / "malformed_ansys.inp"
