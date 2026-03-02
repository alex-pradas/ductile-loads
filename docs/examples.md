# Examples

## Basic workflow

A complete processing pipeline from load delivery to ANSYS export:

```python
from ductile_loads import LoadSet

# Load and convert
ls = LoadSet.read_json("supplier_forces.json")
ls_si = ls.convert_to("N")

# Envelope and export
envelope = ls_si.envelope()
envelope.to_ansys(folder_path="design_loads", name_stem="design_load")

# Reports
print(envelope.envelope_to_markdown(output="envelope.md"))
envelope.get_point_extremes(output="envelope_extremes.json")
```

## Applying a safety factor

Scale all loads by a factor before exporting:

```python
from ductile_loads import LoadSet

ls = LoadSet.read_json("supplier_forces.json")
ls_si = ls.convert_to("N")

# Apply 1.5x ultimate factor
ls_ultimate = ls_si.factor(1.5)

ls_ultimate.to_ansys(folder_path="ultimate_loads", name_stem="ultimate_load")
```

## Comparing two load deliveries

Compare a new delivery against a previous one:

```python
from ductile_loads import LoadSet

# Load both versions
ls_old = LoadSet.read_json("chassis_loads_r1.json")
ls_new = LoadSet.read_json("chassis_loads_r2.json")

# Convert to same units
ls_old_si = ls_old.convert_to("N")
ls_new_si = ls_new.convert_to("N")

# Create envelopes
env_old = ls_old_si.envelope()
env_new = ls_new_si.envelope()

# Compare (auto-converts units if needed)
comparison = env_old.compare_to(env_new)

# Check if new loads exceed old envelope in any component
if comparison.new_exceeds_old():
    print("New loads exceed old envelope in at least one component")
else:
    print("Old loads fully envelope the new delivery")

# Generate full report with charts
report_path = comparison.generate_comparison_report("reports/")
print(f"Report saved to: {report_path}")
```

## Reading ANSYS files

Read an existing `.inp` file back into a `LoadSet`:

```python
from ductile_loads import LoadSet, Units

ls = LoadSet.read_ansys(
    "design_load_07.inp",
    units=Units(forces="N", moments="Nm"),
    name="Imported from ANSYS",
    version=1,
)

ls.print_head()
```

## Excluding points from ANSYS export

Skip specific points (e.g., damper points) when exporting:

```python
from ductile_loads import LoadSet

ls = LoadSet.read_json("supplier_forces.json").convert_to("N").envelope()

ls.to_ansys(
    folder_path="design_loads",
    name_stem="design_load",
    exclude=["damper", "damper_upper"],
)
```

## Generating the JSON Schema

Export the `LoadSet` JSON Schema for validation or documentation:

```python
from ductile_loads import LoadSet

schema = LoadSet.generate_json_schema(output_file="loadset_schema.json")
```

## Inspecting data

Use the display methods to inspect your data in the terminal (requires `[display]` extra):

```python
from ductile_loads import LoadSet

ls = LoadSet.read_json("supplier_forces.json")

# Preview first 5 load cases
ls.print_head()

# All load cases
ls.print_table()

# Envelope bounds
ls.print_envelope()

# Detailed extremes
ls.print_extremes()
```

## Inline script template

A complete single-file script using `uv`:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["ductile-loads[all]"]
# ///

from ductile_loads import LoadSet

# Load and process
ls = LoadSet.read_json("supplier_forces.json")
ls_si = ls.convert_to("N")
envelope = ls_si.envelope()

# Rename load cases for clean filenames
for lc in envelope.load_cases:
    lc.name = (lc.name or "unnamed").split("_")[-1]

# Export
envelope.to_ansys(folder_path="design_loads", name_stem="design_load", exclude=["damper"])
print(envelope.envelope_to_markdown(output="envelope.md"))
envelope.get_point_extremes(output="envelope_extremes.json")
```

Run with:

```bash
uv run processing.py
```
