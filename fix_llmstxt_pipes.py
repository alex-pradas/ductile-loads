#!/usr/bin/env python3
"""Fix unescaped pipes inside backtick spans in markdown table rows.

mkdocs-llmstxt (via markdownify) doesn't escape | inside code spans
in table cells. This breaks markdown tables wherever Python union types
like `str | None` appear. This script post-processes the generated
llms*.txt files to fix these broken rows.
"""

import re
import sys


def fix_pipes_in_backtick_spans(text: str) -> str:
    lines = text.split("\n")
    fixed = []
    for line in lines:
        if line.startswith("|"):
            # Fix escaped-backtick spans: \`...\`
            # These contain unescaped | that broke the table columns
            line = re.sub(
                r"\\`(.*?)\\`",
                lambda m: "`" + m.group(1).replace("|", r"\|") + "`",
                line,
            )
        fixed.append(line)
    return "\n".join(fixed)


def main():
    for path in sys.argv[1:]:
        with open(path) as f:
            text = f.read()
        fixed = fix_pipes_in_backtick_spans(text)
        with open(path, "w") as f:
            f.write(fixed)
        print(f"Fixed: {path}")


if __name__ == "__main__":
    main()
