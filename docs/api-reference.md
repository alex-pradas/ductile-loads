# API Reference

All public classes are importable from the top-level package:

```python
from ductile_loads import (
    ForceMoment, PointLoad, LoadCase, Units, LoadSet,
    ComparisonRow, LoadSetCompare,
)
```

---

## Data Models

### ForceMoment

Six-component force/moment vector at a point.

```python
class ForceMoment(BaseModel):
    fx: float = 0.0
    fy: float = 0.0
    fz: float = 0.0
    mx: float = 0.0
    my: float = 0.0
    mz: float = 0.0
```

All fields default to `0.0`.

### PointLoad

A named point with a force/moment vector.

```python
class PointLoad(BaseModel):
    name: str | None = None
    force_moment: ForceMoment
```

### LoadCase

A named load case containing point loads.

```python
class LoadCase(BaseModel):
    name: str | None = None
    description: str | None = None
    point_loads: list[PointLoad] = []
```

### Units

Force and moment unit pair.

```python
class Units(BaseModel):
    forces: "N" | "kN" | "klbs" = "N"
    moments: "Nmm" | "Nm" | "kNm" | "klbs.in" = "Nm"
```

### LoadSet

Top-level model: a versioned collection of load cases with units. This is the main class you interact with.

```python
class LoadSet(BaseModel):
    name: str | None
    description: str | None = None
    version: int
    units: Units
    loads_type: "limit" | "ultimate" | None = None
    load_cases: list[LoadCase]
```

---

## LoadSet Methods

### I/O

#### `LoadSet.read_json(file_path) -> LoadSet`

Class method. Read a LoadSet from a JSON file.

**Parameters:**

- `file_path` — path to the JSON file

**Returns:** `LoadSet` instance

**Raises:** `FileNotFoundError`, `json.JSONDecodeError`, `ValueError`

---

#### `LoadSet.read_ansys(file_path, units, name=None, version=1) -> LoadSet`

Class method. Read a LoadSet from an ANSYS `.inp` file.

Parses ANSYS APDL load files with `/TITLE`, `cmsel,s,pilot_*`, and `f,all,*` commands.

**Parameters:**

- `file_path` — path to the `.inp` file
- `units` — `Units` instance specifying force and moment units
- `name` — optional name (defaults to filename stem)
- `version` — version number (default: 1)

**Returns:** `LoadSet` with a single `LoadCase`

**Raises:** `FileNotFoundError`, `ValueError`

---

#### `loadset.to_json(file_path=None, indent=2) -> str`

Write the LoadSet to a JSON file and/or return the JSON string.

**Parameters:**

- `file_path` — optional output path. If `None`, only returns the string
- `indent` — JSON indentation level (default: 2)

**Returns:** JSON string

---

#### `loadset.to_ansys(folder_path="temp", name_stem=None, exclude=None) -> None`

Export the LoadSet to ANSYS `.inp` files (one per load case).

Creates the output folder if needed and cleans any existing files in it.

**Parameters:**

- `folder_path` — output directory (default: `"temp"`)
- `name_stem` — optional prefix for filenames. If `None`, uses only load case names
- `exclude` — list of point names to omit from export

---

#### `LoadSet.generate_json_schema(output_file=None) -> dict`

Class method. Generate the JSON Schema for the LoadSet model.

**Parameters:**

- `output_file` — optional path to write the schema file

**Returns:** JSON Schema as a dictionary

---

### Processing

#### `loadset.convert_to(units) -> LoadSet`

Convert all force and moment values to the target unit system.

The force unit determines the paired moment unit automatically:

| Force | Moment |
|-------|--------|
| `"N"` | `"Nm"` |
| `"kN"` | `"kNm"` |
| `"klbs"` | `"klbs.in"` |

**Parameters:**

- `units` — target force unit: `"N"`, `"kN"`, or `"klbs"`

**Returns:** new `LoadSet` with converted values

**Conversion factors:** 1 klbs = 4448.22 N, 1 klbs.in = 112.98 Nm

---

#### `loadset.factor(by) -> LoadSet`

Scale all force and moment values by a factor.

**Parameters:**

- `by` — scale factor (float)

**Returns:** new `LoadSet` with scaled values

---

#### `loadset.envelope() -> LoadSet`

Create an envelope LoadSet containing only load cases with extreme values.

For each point and component, selects load cases with:

- **Maximum value** — always included
- **Minimum value** — only if negative

Load cases appearing in multiple extremes are deduplicated.

**Returns:** new `LoadSet` with the reduced set of critical load cases

**Raises:** `ValueError` if the LoadSet has no load cases

---

### Analysis

#### `loadset.get_point_extremes(output=None) -> dict`

Get extreme values (max/min) for each point and component across all load cases.

Components where both max and min are zero are filtered out.

**Parameters:**

- `output` — optional file path to write the extremes as JSON

**Returns:** nested dictionary:

```python
{
    "point_name": {
        "fx": {
            "max": {"value": 100.0, "loadcase": "Case_A"},
            "min": {"value": -20.0, "loadcase": "Case_C"}
        },
        ...
    }
}
```

---

#### `loadset.compare_to(other) -> LoadSetCompare`

Compare this LoadSet's envelope to another LoadSet's envelope.

Auto-converts units if they differ (converts `other` to match `self`).

**Parameters:**

- `other` — the `LoadSet` to compare against

**Returns:** `LoadSetCompare` with detailed comparison results

---

### Display

These methods require the `[display]` or `[all]` extra (`rich`).

#### `loadset.print_head(n=5) -> None`

Print a preview of the first `n` load cases as a formatted Rich table.

#### `loadset.print_table() -> None`

Print all load cases as a formatted Rich table.

#### `loadset.print_extremes() -> None`

Print extreme values per point and component as a Rich table.

#### `loadset.print_envelope() -> None`

Print envelope summary in wide format (one max/min row per point).

#### `loadset.envelope_to_markdown(output=None) -> str`

Return the envelope summary as a Markdown table. Optionally writes to a file.

**Parameters:**

- `output` — optional file path to write the Markdown

**Returns:** Markdown string

---

## LoadSetCompare

Returned by `loadset.compare_to(other)`. Contains the comparison results between two LoadSets.

```python
class LoadSetCompare(BaseModel):
    loadset1_metadata: dict
    loadset2_metadata: dict
    comparison_rows: list[ComparisonRow]
```

### ComparisonRow

```python
class ComparisonRow(BaseModel):
    point_name: str
    component: "fx" | "fy" | "fz" | "mx" | "my" | "mz"
    type: "max" | "min"
    loadset1_value: float
    loadset2_value: float
    loadset1_loadcase: str
    loadset2_loadcase: str
    abs_diff: float
    pct_diff: float  # percentage relative to loadset1
```

### Methods

#### `compare.to_dict() -> dict`

Convert the comparison to a dictionary.

---

#### `compare.to_json(indent=2) -> str`

Export the comparison as a JSON string.

---

#### `compare.new_exceeds_old() -> bool`

Check if `loadset2` (new) exceeds `loadset1` (old) in any comparison:

- For `"max"` type: `loadset2_value > loadset1_value`
- For `"min"` type: `loadset2_value < loadset1_value` (more negative)

Returns `True` if new loads are more critical in at least one comparison.

---

#### `compare.generate_comparison_report(output_dir, report_name="comparison_report", image_format="png", indent=2) -> Path`

Generate a complete comparison report with JSON data and chart images.

**Parameters:**

- `output_dir` — directory to save report files
- `report_name` — base name for report files (default: `"comparison_report"`)
- `image_format` — `"png"` or `"svg"`
- `indent` — JSON indentation

**Returns:** path to the generated JSON report file

**Requires:** `matplotlib` (`[charts]` or `[all]` extra)

---

#### `compare.generate_range_charts(output_dir=None, image_format="png", as_base64=False) -> dict[str, Path | str]`

Generate range bar charts comparing LoadSets for each point.

Creates dual-subplot figures (forces vs moments) with min-to-max range bars.

**Parameters:**

- `output_dir` — directory to save images (required if `as_base64=False`)
- `image_format` — `"png"` or `"svg"`
- `as_base64` — if `True`, return base64-encoded strings instead of saving files

**Returns:** mapping of point names to file paths (or base64 strings)

**Requires:** `matplotlib` (`[charts]` or `[all]` extra)
