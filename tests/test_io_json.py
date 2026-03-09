"""Tests for JSON read/write, round-trip, and schema generation."""

import json
from pathlib import Path

import pytest

from ductile_loads import LoadSet, Units


class TestReadJson:
    def test_reads_valid_file(self, sample_json_path):
        ls = LoadSet.read_json(sample_json_path)
        assert ls.name == "Sample LoadSet"
        assert ls.version == 1
        assert len(ls.load_cases) == 2
        assert ls.units.forces == "N"
        assert ls.loads_type == "limit"

    def test_preserves_point_values(self, sample_json_path):
        ls = LoadSet.read_json(sample_json_path)
        pa = ls.load_cases[0].point_loads[0]
        assert pa.name == "PointA"
        assert pa.force_moment.fx == 100.0
        assert pa.force_moment.fy == -50.0

    def test_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            LoadSet.read_json(tmp_path / "nonexistent.json")

    def test_invalid_json(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{invalid json")
        with pytest.raises(json.JSONDecodeError):
            LoadSet.read_json(bad)

    def test_invalid_schema(self, tmp_path):
        bad = tmp_path / "bad_schema.json"
        bad.write_text('{"name": "X"}')  # missing required fields
        with pytest.raises(ValueError):
            LoadSet.read_json(bad)


class TestToJson:
    def test_returns_json_string(self, simple_loadset):
        result = simple_loadset.to_json()
        data = json.loads(result)
        assert data["name"] == "Simple"

    def test_writes_file(self, simple_loadset, tmp_path):
        out = tmp_path / "out.json"
        simple_loadset.to_json(file_path=out)
        assert out.exists()
        data = json.loads(out.read_text())
        assert data["version"] == 1

    def test_creates_parent_dirs(self, simple_loadset, tmp_path):
        out = tmp_path / "nested" / "deep" / "out.json"
        simple_loadset.to_json(file_path=out)
        assert out.exists()

    def test_custom_indent(self, simple_loadset):
        result = simple_loadset.to_json(indent=4)
        # 4-space indent should produce "    " in the output
        assert "    " in result


class TestRoundTrip:
    def test_json_round_trip(self, simple_loadset, tmp_path):
        path = tmp_path / "roundtrip.json"
        simple_loadset.to_json(file_path=path)
        loaded = LoadSet.read_json(path)

        assert loaded.name == simple_loadset.name
        assert loaded.version == simple_loadset.version
        assert loaded.units.forces == simple_loadset.units.forces
        assert loaded.units.moments == simple_loadset.units.moments
        assert loaded.loads_type == simple_loadset.loads_type
        assert len(loaded.load_cases) == len(simple_loadset.load_cases)

        for orig_lc, load_lc in zip(
            simple_loadset.load_cases, loaded.load_cases, strict=True
        ):
            assert orig_lc.name == load_lc.name
            for orig_pl, load_pl in zip(
                orig_lc.point_loads, load_lc.point_loads, strict=True
            ):
                assert orig_pl.name == load_pl.name
                for attr in ("fx", "fy", "fz", "mx", "my", "mz"):
                    assert getattr(orig_pl.force_moment, attr) == pytest.approx(
                        getattr(load_pl.force_moment, attr)
                    )


class TestGenerateJsonSchema:
    def test_returns_dict(self):
        schema = LoadSet.generate_json_schema()
        assert isinstance(schema, dict)
        assert "$schema" in schema

    def test_schema_version(self):
        schema = LoadSet.generate_json_schema()
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"

    def test_has_examples(self):
        schema = LoadSet.generate_json_schema()
        assert "examples" in schema
        assert len(schema["examples"]) > 0

    def test_writes_to_file(self, tmp_path):
        out = tmp_path / "schema.json"
        schema = LoadSet.generate_json_schema(output_file=out)
        assert out.exists()
        loaded = json.loads(out.read_text())
        assert loaded == schema

    def test_creates_parent_dirs(self, tmp_path):
        out = tmp_path / "deep" / "schema.json"
        LoadSet.generate_json_schema(output_file=out)
        assert out.exists()
