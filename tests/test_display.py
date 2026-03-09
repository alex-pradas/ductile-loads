"""Tests for display methods (Rich) and envelope_to_markdown().

These are mostly smoke tests — verify they run without error and produce output.
"""

import pytest

rich = pytest.importorskip("rich")


class TestPrintHead:
    def test_runs_without_error(self, simple_loadset, capsys):
        simple_loadset.print_head()
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_custom_n(self, simple_loadset, capsys):
        simple_loadset.print_head(n=1)
        # Should mention "1 of 2"
        captured = capsys.readouterr()
        assert "1" in captured.out

    def test_n_larger_than_total(self, simple_loadset, capsys):
        simple_loadset.print_head(n=100)
        captured = capsys.readouterr()
        assert "all" in captured.out.lower() or "2" in captured.out


class TestPrintTable:
    def test_runs_without_error(self, simple_loadset, capsys):
        simple_loadset.print_table()
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_shows_all_cases(self, simple_loadset, capsys):
        simple_loadset.print_table()
        captured = capsys.readouterr()
        assert "Case_A" in captured.out
        assert "Case_B" in captured.out


class TestPrintExtremes:
    def test_runs_without_error(self, simple_loadset, capsys):
        simple_loadset.print_extremes()
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_shows_points(self, simple_loadset, capsys):
        simple_loadset.print_extremes()
        captured = capsys.readouterr()
        assert "PointA" in captured.out
        assert "PointB" in captured.out

    def test_empty_extremes(self, capsys):
        from ductile_loads import ForceMoment, LoadCase, LoadSet, PointLoad, Units

        ls = LoadSet(
            name="AllZero",
            version=1,
            units=Units(),
            load_cases=[
                LoadCase(
                    name="C",
                    point_loads=[PointLoad(name="P", force_moment=ForceMoment())],
                ),
            ],
        )
        ls.print_extremes()
        captured = capsys.readouterr()
        assert "zero" in captured.out.lower() or "No extreme" in captured.out


class TestPrintEnvelope:
    def test_runs_without_error(self, simple_loadset, capsys):
        simple_loadset.print_envelope()
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_empty_extremes(self, capsys):
        from ductile_loads import ForceMoment, LoadCase, LoadSet, PointLoad, Units

        ls = LoadSet(
            name="AllZero",
            version=1,
            units=Units(),
            load_cases=[
                LoadCase(
                    name="C",
                    point_loads=[PointLoad(name="P", force_moment=ForceMoment())],
                ),
            ],
        )
        ls.print_envelope()
        captured = capsys.readouterr()
        assert "zero" in captured.out.lower() or "No extreme" in captured.out


class TestEnvelopeToMarkdown:
    def test_returns_string(self, simple_loadset):
        md = simple_loadset.envelope_to_markdown()
        assert isinstance(md, str)
        assert len(md) > 0

    def test_has_table_header(self, simple_loadset):
        md = simple_loadset.envelope_to_markdown()
        assert "| Point |" in md
        assert "| Type |" in md or "Type" in md

    def test_contains_point_names(self, simple_loadset):
        md = simple_loadset.envelope_to_markdown()
        assert "PointA" in md
        assert "PointB" in md

    def test_contains_max_min_rows(self, simple_loadset):
        md = simple_loadset.envelope_to_markdown()
        assert "max" in md
        assert "min" in md

    def test_values_correct(self, simple_loadset):
        md = simple_loadset.envelope_to_markdown()
        # PointA fx max is 500.0
        assert "500.000" in md

    def test_writes_to_file(self, simple_loadset, tmp_path):
        out = tmp_path / "envelope.md"
        md = simple_loadset.envelope_to_markdown(output=out)
        assert out.exists()
        assert out.read_text() == md

    def test_empty_extremes(self):
        from ductile_loads import ForceMoment, LoadCase, LoadSet, PointLoad, Units

        ls = LoadSet(
            name="AllZero",
            version=1,
            units=Units(),
            load_cases=[
                LoadCase(
                    name="C",
                    point_loads=[PointLoad(name="P", force_moment=ForceMoment())],
                ),
            ],
        )
        md = ls.envelope_to_markdown()
        assert "No extreme" in md or "all zero" in md.lower()
