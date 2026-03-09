"""Tests for chart generation (matplotlib-dependent)."""

import pytest

plt = pytest.importorskip("matplotlib.pyplot")

from ductile_loads import ForceMoment, LoadCase, LoadSet, PointLoad, Units


@pytest.fixture
def comparison(simple_loadset):
    """A LoadSetCompare between simple_loadset and a scaled version."""
    bigger = simple_loadset.factor(by=1.3)
    return simple_loadset.compare_to(bigger)


@pytest.fixture
def simple_loadset():
    """Override conftest fixture for self-contained chart tests."""
    return LoadSet(
        name="ChartTest",
        version=1,
        units=Units(forces="N", moments="Nm"),
        load_cases=[
            LoadCase(
                name="C1",
                point_loads=[
                    PointLoad(
                        name="P1",
                        force_moment=ForceMoment(fx=100.0, fy=-50.0, mx=10.0),
                    ),
                ],
            ),
            LoadCase(
                name="C2",
                point_loads=[
                    PointLoad(
                        name="P1",
                        force_moment=ForceMoment(fx=-30.0, fy=200.0, mx=-5.0),
                    ),
                ],
            ),
        ],
    )


class TestGenerateRangeCharts:
    def test_base64_output(self, comparison):
        result = comparison.generate_range_charts(as_base64=True)
        assert isinstance(result, dict)
        assert len(result) > 0
        for key, val in result.items():
            assert isinstance(val, str)
            assert len(val) > 100  # base64 strings are long

    def test_file_output(self, comparison, tmp_path):
        result = comparison.generate_range_charts(output_dir=tmp_path)
        assert len(result) > 0
        for point_name, path in result.items():
            assert path.exists()
            assert path.suffix == ".png"

    def test_svg_format(self, comparison, tmp_path):
        result = comparison.generate_range_charts(
            output_dir=tmp_path, image_format="svg"
        )
        for path in result.values():
            assert path.suffix == ".svg"

    def test_invalid_format_raises(self, comparison, tmp_path):
        with pytest.raises(ValueError, match="Unsupported image format"):
            comparison.generate_range_charts(
                output_dir=tmp_path, image_format="bmp"
            )

    def test_no_output_dir_no_base64_raises(self, comparison):
        with pytest.raises(ValueError, match="output_dir is required"):
            comparison.generate_range_charts(as_base64=False, output_dir=None)

    def test_creates_output_dir(self, comparison, tmp_path):
        out = tmp_path / "new_dir"
        comparison.generate_range_charts(output_dir=out)
        assert out.is_dir()


class TestGenerateComparisonReport:
    def test_creates_json_report(self, comparison, tmp_path):
        path = comparison.generate_comparison_report(output_dir=tmp_path)
        assert path.exists()
        assert path.suffix == ".json"

    def test_creates_chart_files(self, comparison, tmp_path):
        comparison.generate_comparison_report(output_dir=tmp_path)
        charts = list(tmp_path.glob("*.png"))
        assert len(charts) > 0

    def test_custom_report_name(self, comparison, tmp_path):
        path = comparison.generate_comparison_report(
            output_dir=tmp_path, report_name="my_report"
        )
        assert path.name == "my_report.json"

    def test_report_json_structure(self, comparison, tmp_path):
        import json

        path = comparison.generate_comparison_report(output_dir=tmp_path)
        data = json.loads(path.read_text())
        assert "report_metadata" in data
        assert "comparisons" in data
        assert "chart_files" in data["report_metadata"]
        assert "new_exceeds_old" in data["report_metadata"]

    def test_svg_format(self, comparison, tmp_path):
        comparison.generate_comparison_report(
            output_dir=tmp_path, image_format="svg"
        )
        svgs = list(tmp_path.glob("*.svg"))
        assert len(svgs) > 0
