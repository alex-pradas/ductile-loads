# ductile-loads

Certified loads processing tool for structural analysis, approved under the Design Quality Management System (DQMS).

`ductile-loads` provides a complete pipeline for processing structural load data: reading load deliveries, converting units, downselecting critical load cases via envelope analysis, exporting to ANSYS, and comparing load sets across revisions.

This is a sample tool as part of the DUCTILE agentic orchestration paper. See the [DUCTILE repository](https://github.com/alex-pradas/DUCTILE) or the paper (DOI: TBD) for context.

## Installation

```
uv add ductile-loads
```

## Quick start

```
from ductile_loads import LoadSet

# Load load delivery
ls = LoadSet.read_json("supplier_forces.json")

# Convert to SI units
ls = ls.convert_to("N")

# Downselect to critical load cases
ls_env = ls.envelope()

# Export to ANSYS
ls_env.to_ansys(folder_path="design_loads", name_stem="design_load")

# Get envelope extremes
extremes = ls_env.get_point_extremes(output="envelope_extremes.json")
```

## Key features

- **Pydantic data models** — validated, serializable load data structures
- **Unit conversion** — N/kN/klbs with automatic moment unit pairing
- **Envelope analysis** — downselect to load cases containing extreme values
- **ANSYS export** — generate `.inp` files with force commands per load case
- **Load comparison** — compare two load deliveries with charts and reports
- **Rich display** — formatted tables for terminal inspection (requires `[display]`)
- **Markdown output** — envelope summaries as Markdown tables

## License

MIT
