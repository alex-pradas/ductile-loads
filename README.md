# ductile-loads

Loads processing tool for structural analysis, certified under the Design Quality Management System (DQMS).

Part of the paper: *"DUCTILE: Agentic LLM Orchestration of Engineering Analysis in Product Development Practice"* — [github.com/alex-pradas/DUCTILE](https://github.com/alex-pradas/DUCTILE)

## Install

```bash
pip install ductile-loads
```

With optional display/chart features:

```bash
pip install ductile-loads[all]
```

## Quick Start

```python
from ductile_loads import LoadSet

# Load data
ls = LoadSet.read_json("OEM_loads.json")

# Convert units
ls = ls.convert_to("N")

# Envelope (downselect critical load cases)
ls_env = ls.envelope()

# Export to ANSYS
ls_env.to_ansys(folder_path="limit_loads", name_stem="limit_load")

# Get extremes
extremes = ls_env.get_point_extremes(output="envelope_extremes.json")
```

## API Reference

The full API reference is bundled as `llms.txt` inside the package, designed for both human and LLM consumption.

## License

MIT
