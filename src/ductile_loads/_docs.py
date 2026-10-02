"""The package's own copy of the full documentation (llms-full.txt), for offline use."""

from importlib.resources import files
from pathlib import Path

_DOCS = "llms-full.txt"


def api_reference_path() -> Path:
    """Path to the full documentation (llms-full.txt) shipped with the installed package."""
    return Path(str(files("ductile_loads").joinpath(_DOCS)))


def api_reference() -> str:
    """The full documentation (llms-full.txt) of the installed version, as text.

    It is the same text as the documentation site's llms-full.txt for this release,
    so it always matches the installed code.
    """
    return files("ductile_loads").joinpath(_DOCS).read_text(encoding="utf-8")
