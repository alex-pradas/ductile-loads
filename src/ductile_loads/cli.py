"""Command-line entry point: `ductile-loads docs` prints the installed version's documentation."""

import argparse
import sys
from importlib.metadata import version

from ._docs import api_reference, api_reference_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ductile-loads",
        description="Loads processing tool for structural analysis.",
    )
    parser.add_argument("--version", action="version", version=f"ductile-loads {version('ductile-loads')}")
    sub = parser.add_subparsers(dest="command", required=True)
    p_docs = sub.add_parser(
        "docs",
        help="Print the full documentation (llms-full.txt) of the installed version",
    )
    p_docs.add_argument("--path", action="store_true", help="Print the file's path instead of its text")
    args = parser.parse_args(argv)

    if args.command == "docs":
        sys.stdout.write(f"{api_reference_path()}\n" if args.path else api_reference())
    return 0


if __name__ == "__main__":
    sys.exit(main())
