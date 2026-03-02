# Getting Started

## Installation

### With uv

```bash
uv add ductile-loads
```

### Optional dependencies

`ductile-loads` has optional extras for display and charting:

| Extra | Packages | Use case |
|-------|----------|----------|
| `display` | `rich` | Formatted terminal tables |
| `charts` | `matplotlib` | Comparison range charts |
| `all` | `rich`, `matplotlib` | Everything |

```bash
uv add ductile-loads[all]
```

### With uv (inline script)

For single-file scripts, use [PEP 723](https://peps.python.org/pep-0723/) inline metadata:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["ductile-loads[all]"]
# ///

from ductile_loads import LoadSet

ls = LoadSet.read_json("supplier_forces.json")
ls.print_head()
```

Run with:

```bash
uv run my_script.py
```

`uv` will automatically install `ductile-loads` and its dependencies in an isolated environment.

## Your first script

Here is a minimal processing script that loads an load delivery, converts units, creates an envelope, and exports to ANSYS:

```python
from ductile_loads import LoadSet

# 1. Read the load delivery
loadset = LoadSet.read_json("supplier_forces.json")

# 2. Convert to target units (N and Nm)
loadset_si = loadset.convert_to("N")

# 3. Create envelope (keeps only critical load cases)
envelope = loadset_si.envelope()

# 4. Export to ANSYS .inp files
envelope.to_ansys(
    folder_path="design_loads",
    name_stem="design_load",
    exclude=["damper"],  # skip damper points
)

# 5. Save envelope summary
print(envelope.envelope_to_markdown(output="envelope.md"))

# 6. Save extremes as JSON
envelope.get_point_extremes(output="envelope_extremes.json")
```

### What each step does

1. **`read_json`** parses the JSON file and validates it against the `LoadSet` schema
2. **`convert_to("N")`** converts all force/moment values to SI units (N and Nm), returning a new `LoadSet`
3. **`envelope()`** identifies load cases with extreme values (max, and min if negative) across all points and components, returning a reduced `LoadSet`
4. **`to_ansys`** writes one `.inp` file per load case with ANSYS `F` commands
5. **`envelope_to_markdown`** produces a Markdown table summarizing the envelope bounds
6. **`get_point_extremes`** extracts per-point, per-component max/min values with load case traceability

## Supported units

The `convert_to` method accepts a force unit and automatically pairs it with the corresponding moment unit:

| Force unit | Moment unit | System |
|------------|-------------|--------|
| `"N"` | `"Nm"` | SI |
| `"kN"` | `"kNm"` | SI (kilo) |
| `"klbs"` | `"klbs.in"` | Imperial |

Conversion factors: 1 klbs = 4448.22 N, 1 klbs.in = 112.98 Nm.
