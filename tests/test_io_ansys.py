"""Tests for ANSYS read/write, file content verification, and edge cases."""

from pathlib import Path

import pytest

from ductile_loads import LoadSet, Units


class TestReadAnsys:
    def test_reads_valid_file(self, sample_ansys_path):
        ls = LoadSet.read_ansys(sample_ansys_path, units=Units(forces="N", moments="Nm"))
        assert ls.name == "simple_ansys"  # defaults to filename stem
        assert len(ls.load_cases) == 1

    def test_parses_title(self, sample_ansys_path):
        ls = LoadSet.read_ansys(sample_ansys_path, units=Units())
        assert ls.load_cases[0].name == "TestCase_001"

    def test_parses_points(self, sample_ansys_path):
        ls = LoadSet.read_ansys(sample_ansys_path, units=Units())
        names = [pl.name for pl in ls.load_cases[0].point_loads]
        assert "PointA" in names
        assert "PointB" in names

    def test_parses_values(self, sample_ansys_path):
        ls = LoadSet.read_ansys(sample_ansys_path, units=Units())
        point_a = ls.load_cases[0].point_loads[0]
        assert point_a.force_moment.fx == pytest.approx(100.0)
        assert point_a.force_moment.fy == pytest.approx(-50.0)
        assert point_a.force_moment.fz == pytest.approx(200.0)
        assert point_a.force_moment.mx == pytest.approx(10.0)
        assert point_a.force_moment.my == pytest.approx(-20.0)
        assert point_a.force_moment.mz == pytest.approx(0.0)  # not in file, defaults

    def test_custom_name(self, sample_ansys_path):
        ls = LoadSet.read_ansys(sample_ansys_path, units=Units(), name="Custom")
        assert ls.name == "Custom"

    def test_custom_version(self, sample_ansys_path):
        ls = LoadSet.read_ansys(sample_ansys_path, units=Units(), version=42)
        assert ls.version == 42

    def test_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            LoadSet.read_ansys(tmp_path / "missing.inp", units=Units())

    def test_malformed_value(self, malformed_ansys_path):
        with pytest.raises(ValueError, match="Invalid numeric value"):
            LoadSet.read_ansys(malformed_ansys_path, units=Units())

    def test_no_title(self, tmp_path):
        f = tmp_path / "no_title.inp"
        f.write_text("cmsel,s,pilot_P1\nf,all,fx,1.0\n")
        with pytest.raises(ValueError, match="No /TITLE"):
            LoadSet.read_ansys(f, units=Units())

    def test_no_point_loads(self, tmp_path):
        f = tmp_path / "no_loads.inp"
        f.write_text("/TITLE,Empty\n")
        with pytest.raises(ValueError, match="No point loads"):
            LoadSet.read_ansys(f, units=Units())

    def test_force_without_point(self, tmp_path):
        f = tmp_path / "orphan_force.inp"
        f.write_text("/TITLE,Bad\nf,all,fx,100.0\n")
        with pytest.raises(ValueError, match="without preceding point"):
            LoadSet.read_ansys(f, units=Units())

    def test_invalid_component(self, tmp_path):
        f = tmp_path / "bad_comp.inp"
        f.write_text("/TITLE,Bad\ncmsel,s,pilot_P1\nf,all,fq,1.0\n")
        with pytest.raises(ValueError, match="Invalid component"):
            LoadSet.read_ansys(f, units=Units())

    def test_comments_skipped(self, tmp_path):
        f = tmp_path / "comments.inp"
        f.write_text(
            "/TITLE,WithComments\n"
            "! this is a comment\n"
            "cmsel,s,pilot_P1\n"
            "f,all,fx,5.0\n"
        )
        ls = LoadSet.read_ansys(f, units=Units())
        assert ls.load_cases[0].point_loads[0].force_moment.fx == pytest.approx(5.0)

    def test_scientific_notation(self, tmp_path):
        f = tmp_path / "sci.inp"
        f.write_text(
            "/TITLE,SciNotation\n"
            "cmsel,s,pilot_P1\n"
            "f,all,fx,1.234e+03\n"
            "f,all,fy,-5.678e-02\n"
        )
        ls = LoadSet.read_ansys(f, units=Units())
        pl = ls.load_cases[0].point_loads[0]
        assert pl.force_moment.fx == pytest.approx(1234.0)
        assert pl.force_moment.fy == pytest.approx(-0.05678)


class TestToAnsys:
    def test_creates_files(self, simple_loadset, tmp_path):
        out = tmp_path / "ansys_out"
        simple_loadset.to_ansys(folder_path=out)
        files = list(out.glob("*.inp"))
        assert len(files) == 2  # one per load case

    def test_file_naming_without_stem(self, simple_loadset, tmp_path):
        out = tmp_path / "ansys_out"
        simple_loadset.to_ansys(folder_path=out)
        names = sorted(f.name for f in out.glob("*.inp"))
        assert names == ["Case_A.inp", "Case_B.inp"]

    def test_file_naming_with_stem(self, simple_loadset, tmp_path):
        out = tmp_path / "ansys_out"
        simple_loadset.to_ansys(folder_path=out, name_stem="design")
        names = sorted(f.name for f in out.glob("*.inp"))
        assert names == ["design_Case_A.inp", "design_Case_B.inp"]

    def test_content_has_title(self, simple_loadset, tmp_path):
        out = tmp_path / "ansys_out"
        simple_loadset.to_ansys(folder_path=out)
        content = (out / "Case_A.inp").read_text()
        assert "/TITLE,Case_A" in content

    def test_content_has_pilot_prefix(self, simple_loadset, tmp_path):
        out = tmp_path / "ansys_out"
        simple_loadset.to_ansys(folder_path=out)
        content = (out / "Case_A.inp").read_text()
        assert "cmsel,s,pilot_PointA" in content
        assert "cmsel,s,pilot_PointB" in content

    def test_content_scientific_notation(self, simple_loadset, tmp_path):
        out = tmp_path / "ansys_out"
        simple_loadset.to_ansys(folder_path=out)
        content = (out / "Case_A.inp").read_text()
        # fx=100.0 → 1.000e+02
        assert "f,all,fx,1.000e+02" in content

    def test_zero_components_omitted(self, simple_loadset, tmp_path):
        out = tmp_path / "ansys_out"
        simple_loadset.to_ansys(folder_path=out)
        content = (out / "Case_A.inp").read_text()
        # PointA has mz=0.0 → should not appear
        lines = content.split("\n")
        point_a_section = []
        in_section = False
        for line in lines:
            if "pilot_PointA" in line:
                in_section = True
            elif in_section and ("pilot_" in line or line.strip() == "alls"):
                break
            elif in_section:
                point_a_section.append(line)
        assert not any("mz" in l for l in point_a_section)

    def test_component_order(self, simple_loadset, tmp_path):
        """Verify ANSYS component order: fx, fy, mx, my, mz, fz."""
        out = tmp_path / "ansys_out"
        simple_loadset.to_ansys(folder_path=out)
        content = (out / "Case_A.inp").read_text()
        lines = content.split("\n")
        # Extract f,all lines for PointA
        in_point_a = False
        components = []
        for line in lines:
            if "pilot_PointA" in line:
                in_point_a = True
                continue
            if in_point_a and line.startswith("f,all,"):
                comp = line.split(",")[2]
                components.append(comp)
            elif in_point_a and line.startswith("nsel"):
                break
        # Expected order for non-zero: fx, fy, mx, my, fz
        assert components == ["fx", "fy", "mx", "my", "fz"]

    def test_exclude_points(self, simple_loadset, tmp_path):
        out = tmp_path / "ansys_out"
        simple_loadset.to_ansys(folder_path=out, exclude=["PointB"])
        content = (out / "Case_A.inp").read_text()
        assert "pilot_PointA" in content
        assert "pilot_PointB" not in content

    def test_cleans_existing_files(self, simple_loadset, tmp_path):
        out = tmp_path / "ansys_out"
        out.mkdir()
        (out / "old_file.inp").write_text("old")
        simple_loadset.to_ansys(folder_path=out)
        assert not (out / "old_file.inp").exists()

    def test_creates_folder(self, simple_loadset, tmp_path):
        out = tmp_path / "new_folder"
        simple_loadset.to_ansys(folder_path=out)
        assert out.is_dir()

    def test_not_a_directory_raises(self, simple_loadset, tmp_path):
        fake = tmp_path / "fake_dir"
        fake.write_text("not a dir")
        with pytest.raises(FileNotFoundError):
            simple_loadset.to_ansys(folder_path=fake)

    def test_empty_loadset_no_files(self, empty_loadset, tmp_path):
        out = tmp_path / "empty_out"
        empty_loadset.to_ansys(folder_path=out)
        assert list(out.glob("*.inp")) == []

    def test_ends_with_alls(self, simple_loadset, tmp_path):
        out = tmp_path / "ansys_out"
        simple_loadset.to_ansys(folder_path=out)
        content = (out / "Case_A.inp").read_text()
        assert content.rstrip().endswith("alls")


def _renamed(loadset: LoadSet, names: list[str]) -> LoadSet:
    """Copy of a LoadSet with its load cases renamed in order."""
    cases = [lc.model_copy(update={"name": n}) for lc, n in zip(loadset.load_cases, names)]
    return loadset.model_copy(update={"load_cases": cases})


class TestToAnsysFileName:
    def test_number_template_keeps_title(self, simple_loadset, tmp_path):
        ls = _renamed(simple_loadset, ["Limit_2", "Limit_20"])
        ls.to_ansys(folder_path=tmp_path, file_name="limit_load_{number}.inp")
        assert sorted(f.name for f in tmp_path.glob("*.inp")) == ["limit_load_2.inp", "limit_load_20.inp"]
        assert (tmp_path / "limit_load_2.inp").read_text().startswith("/TITLE,Limit_2\n")

    def test_name_and_index_fields(self, simple_loadset, tmp_path):
        simple_loadset.to_ansys(folder_path=tmp_path, file_name="{index:02d}_{name}")
        assert sorted(f.name for f in tmp_path.glob("*.inp")) == ["01_Case_A.inp", "02_Case_B.inp"]

    def test_number_is_an_integer(self, simple_loadset, tmp_path):
        ls = _renamed(simple_loadset, ["Limit_002", "Limit_3"])
        ls.to_ansys(folder_path=tmp_path, file_name="lc{number:03d}")
        assert sorted(f.name for f in tmp_path.glob("*.inp")) == ["lc002.inp", "lc003.inp"]

    def test_callable(self, simple_loadset, tmp_path):
        simple_loadset.to_ansys(folder_path=tmp_path, file_name=lambda lc: lc.name.lower())
        assert sorted(f.name for f in tmp_path.glob("*.inp")) == ["case_a.inp", "case_b.inp"]
        assert "/TITLE,Case_A" in (tmp_path / "case_a.inp").read_text()

    def test_with_name_stem_raises(self, simple_loadset, tmp_path):
        with pytest.raises(ValueError, match="either file_name or name_stem"):
            simple_loadset.to_ansys(folder_path=tmp_path, name_stem="x", file_name="{name}")

    def test_number_missing_raises_and_writes_nothing(self, simple_loadset, tmp_path):
        out = tmp_path / "out"
        out.mkdir()
        (out / "keep.inp").write_text("old")
        with pytest.raises(ValueError, match="does not end in a number"):
            simple_loadset.to_ansys(folder_path=out, file_name="limit_load_{number}")
        assert (out / "keep.inp").exists()  # the folder is untouched on a naming error

    def test_unknown_field_raises(self, simple_loadset, tmp_path):
        with pytest.raises(ValueError, match="unknown fields"):
            simple_loadset.to_ansys(folder_path=tmp_path, file_name="{id}")

    def test_duplicate_names_raise(self, simple_loadset, tmp_path):
        with pytest.raises(ValueError, match="same file name"):
            simple_loadset.to_ansys(folder_path=tmp_path, file_name="same")

    def test_path_separator_raises(self, simple_loadset, tmp_path):
        with pytest.raises(ValueError, match="bare file name"):
            simple_loadset.to_ansys(folder_path=tmp_path, file_name="sub/{name}")


class TestPilotPrefixWarning:
    def _with_point_name(self, loadset: LoadSet, name: str) -> LoadSet:
        case = loadset.load_cases[0]
        points = [case.point_loads[0].model_copy(update={"name": name}), *case.point_loads[1:]]
        return loadset.model_copy(update={"load_cases": [case.model_copy(update={"point_loads": points})]})

    def test_warns_on_double_prefix(self, simple_loadset, tmp_path):
        ls = self._with_point_name(simple_loadset, "pilot_lug_port")
        with pytest.warns(UserWarning, match="pilot_pilot_lug_port"):
            ls.to_ansys(folder_path=tmp_path)
        assert "cmsel,s,pilot_pilot_lug_port" in (tmp_path / "Case_A.inp").read_text()

    def test_no_warning_for_excluded_point(self, simple_loadset, tmp_path, recwarn):
        ls = self._with_point_name(simple_loadset, "pilot_bearing")
        ls.to_ansys(folder_path=tmp_path, exclude=["pilot_bearing"])
        assert not [w for w in recwarn if "pilot_" in str(w.message)]

    def test_no_warning_for_plain_names(self, simple_loadset, tmp_path, recwarn):
        simple_loadset.to_ansys(folder_path=tmp_path)
        assert not [w for w in recwarn if "pilot_" in str(w.message)]
