# ductile-loads

Loads processing tool for structural analysis, certified under the Design Quality Management System (DQMS).

This is a sample tool as part of the DUCTILE agentic orchestration paper. See the [DUCTILE repository](https://github.com/alex-pradas/DUCTILE) or the paper (DOI: TBD) for context.

## Documentation

Full documentation: [alex-pradas.github.io/ductile-loads](https://alex-pradas.github.io/ductile-loads)

## Install

```bash
uv add ductile-loads
```

With optional display/chart features:

```bash
uv add ductile-loads[all]
```

## Quick Start

```python
from ductile_loads import LoadSet

# Load data
ls = LoadSet.read_json("supplier_forces.json")

# Convert units
ls = ls.convert_to("N")

# Envelope (downselect critical load cases)
ls_env = ls.envelope()

# Export to ANSYS
ls_env.to_ansys(folder_path="design_loads", name_stem="design_load")

# Get extremes
extremes = ls_env.get_point_extremes(output="envelope_extremes.json")
```

## License

MIT
