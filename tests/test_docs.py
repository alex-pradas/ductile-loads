"""The documentation shipped with the package, and the `ductile-loads docs` command."""

import subprocess
import sys
from importlib.metadata import version

import ductile_loads
from ductile_loads import api_reference, api_reference_path
from ductile_loads.cli import main


def test_packaged_docs_match_installed_version():
    # scripts/build_package_docs.py writes the version on the first line; a stale copy fails here
    assert api_reference().splitlines()[0].startswith(f"ductile-loads {version('ductile-loads')}:")


def test_packaged_docs_cover_the_api():
    text = api_reference()
    for name in ("to_ansys", "file_name", "envelope", "convert_to", "get_point_extremes", "compare_to"):
        assert name in text


def test_path_points_to_the_same_text():
    assert api_reference_path().read_text(encoding="utf-8") == api_reference()


def test_version_attribute():
    assert ductile_loads.__version__ == version("ductile-loads")


def test_cli_docs_prints_text(capsys):
    assert main(["docs"]) == 0
    assert capsys.readouterr().out == api_reference()


def test_cli_docs_path(capsys):
    assert main(["docs", "--path"]) == 0
    assert capsys.readouterr().out.strip() == str(api_reference_path())


def test_python_m_entry_point():
    out = subprocess.run(
        [sys.executable, "-m", "ductile_loads", "docs"], capture_output=True, text=True, check=True
    ).stdout
    assert out == api_reference()
