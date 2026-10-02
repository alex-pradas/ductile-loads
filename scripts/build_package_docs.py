#!/usr/bin/env python3
"""Build the docs site and copy its llms-full.txt into the package.

The package ships the same full documentation as the site, so `ductile-loads docs` prints
the documentation of the installed version. Run after any change to the docs or docstrings:

    uv run --extra docs python scripts/build_package_docs.py

CI rebuilds it and fails if the committed copy differs.
"""

import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from fix_llmstxt_pipes import fix_pipes_in_backtick_spans  # noqa: E402

TARGET = ROOT / "src" / "ductile_loads" / "llms-full.txt"


def main() -> None:
    subprocess.run(["mkdocs", "build", "--quiet"], cwd=ROOT, check=True)
    text = fix_pipes_in_backtick_spans((ROOT / "site" / "llms-full.txt").read_text(encoding="utf-8"))
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    header = (
        f"ductile-loads {version}: full documentation (llms-full.txt), shipped with the installed "
        "package. Print it with `ductile-loads docs`.\n\n"
    )
    TARGET.write_text(header + text, encoding="utf-8")
    print(f"Wrote {TARGET.relative_to(ROOT)} for ductile-loads {version}")


if __name__ == "__main__":
    main()
