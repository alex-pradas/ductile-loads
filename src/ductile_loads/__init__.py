from importlib.metadata import PackageNotFoundError, version

from ._docs import api_reference, api_reference_path
from .loads import (
    ComparisonRow,
    ForceMoment,
    LoadCase,
    LoadSet,
    LoadSetCompare,
    PointLoad,
    Units,
)

__all__ = [
    "api_reference",
    "api_reference_path",
    "ComparisonRow",
    "ForceMoment",
    "LoadCase",
    "LoadSet",
    "LoadSetCompare",
    "PointLoad",
    "Units",
]

try:
    __version__ = version("ductile-loads")
except PackageNotFoundError:  # running from a source tree without an install
    __version__ = "0+unknown"
