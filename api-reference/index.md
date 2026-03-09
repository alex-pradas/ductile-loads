# API Reference

All public classes are importable from the top-level package:

```
from ductile_loads import (
    ForceMoment, PointLoad, LoadCase, Units, LoadSet,
    ComparisonRow, LoadSetCompare,
)
```

______________________________________________________________________

## Data Models

### `ductile_loads.ForceMoment`

Six-component force/moment vector at a point.

Contains three force components (fx, fy, fz) and three moment components (mx, my, mz). All default to zero.

### `ductile_loads.PointLoad`

A named structural point with an associated force/moment vector.

Attributes:

| Name           | Type          | Description                                          |
| -------------- | ------------- | ---------------------------------------------------- |
| `name`         | \`str         | None\`                                               |
| `force_moment` | `ForceMoment` | The six-component force/moment vector at this point. |

### `ductile_loads.LoadCase`

A named load case containing point loads.

Represents a single loading condition (e.g. a manoeuvre or gust case) applied to one or more structural points.

Attributes:

| Name          | Type              | Description                             |
| ------------- | ----------------- | --------------------------------------- |
| `name`        | \`str             | None\`                                  |
| `description` | \`str             | None\`                                  |
| `point_loads` | `list[PointLoad]` | The point loads belonging to this case. |

### `ductile_loads.Units`

Force and moment unit pair.

Attributes:

| Name      | Type         | Description                                            |
| --------- | ------------ | ------------------------------------------------------ |
| `forces`  | `ForceUnit`  | Force unit — one of "N", "kN", or "klbs".              |
| `moments` | `MomentUnit` | Moment unit — one of "Nmm", "Nm", "kNm", or "klbs.in". |

______________________________________________________________________

## LoadSet

### `ductile_loads.LoadSet`

Top-level model: a versioned collection of load cases with units.

This is the main entry point for working with structural load data. Supports reading/writing JSON and ANSYS formats, unit conversion, envelope analysis, and comparison between load sets.

Attributes:

| Name          | Type                           | Description                                        |
| ------------- | ------------------------------ | -------------------------------------------------- |
| `name`        | \`str                          | None\`                                             |
| `description` | \`str                          | None\`                                             |
| `version`     | `int`                          | Integer version number for tracking revisions.     |
| `units`       | `Units`                        | Force and moment units for all values in this set. |
| `loads_type`  | \`Literal['limit', 'ultimate'] | None\`                                             |
| `load_cases`  | `list[LoadCase]`               | The load cases in this set.                        |

#### `generate_json_schema(output_file=None)`

Generate JSON Schema for LoadSet model.

Parameters:

| Name          | Type       | Description | Default                               |
| ------------- | ---------- | ----------- | ------------------------------------- |
| `output_file` | \`PathLike | None\`      | Optional path to save the schema file |

Returns:

| Name   | Type   | Description                   |
| ------ | ------ | ----------------------------- |
| `dict` | `dict` | JSON Schema for LoadSet model |

Raises:

| Type                | Description                       |
| ------------------- | --------------------------------- |
| `FileNotFoundError` | If output directory doesn't exist |
| `ValueError`        | If schema generation fails        |

#### `read_json(file_path)`

Read a LoadSet from a JSON file.

Parameters:

| Name        | Type       | Description                   | Default    |
| ----------- | ---------- | ----------------------------- | ---------- |
| `file_path` | `PathLike` | Path to the JSON file to read | *required* |

Returns:

| Name      | Type      | Description                 |
| --------- | --------- | --------------------------- |
| `LoadSet` | `LoadSet` | The loaded LoadSet instance |

Raises:

| Type                | Description                          |
| ------------------- | ------------------------------------ |
| `FileNotFoundError` | If the file doesn't exist            |
| `JSONDecodeError`   | If the JSON is invalid               |
| `ValueError`        | If the data doesn't match the schema |

#### `to_json(file_path=None, indent=2)`

Write LoadSet to a JSON file and/or return JSON string.

Parameters:

| Name        | Type  | Description                         | Default |
| ----------- | ----- | ----------------------------------- | ------- |
| `file_path` | \`str | PathLike                            | None\`  |
| `indent`    | `int` | JSON indentation level (default: 2) | `2`     |

Returns:

| Name  | Type  | Description                        |
| ----- | ----- | ---------------------------------- |
| `str` | `str` | JSON representation of the LoadSet |

Raises:

| Type                | Description                           |
| ------------------- | ------------------------------------- |
| `FileNotFoundError` | If the output directory doesn't exist |
| `ValueError`        | If serialization fails                |

#### `convert_to(units)`

Convert all force and moment values to the target unit system.

The force unit determines the paired moment unit automatically:

| Force    | Moment      |
| -------- | ----------- |
| `"N"`    | `"Nm"`      |
| `"kN"`   | `"kNm"`     |
| `"klbs"` | `"klbs.in"` |

Conversion factors: 1 klbs = 4448.22 N, 1 klbs.in = 112.98 Nm.

Parameters:

| Name    | Type        | Description        | Default    |
| ------- | ----------- | ------------------ | ---------- |
| `units` | `ForceUnit` | Target force unit. | *required* |

Returns:

| Type      | Description                          |
| --------- | ------------------------------------ |
| `LoadSet` | A new LoadSet with converted values. |

Raises:

| Type         | Description                          |
| ------------ | ------------------------------------ |
| `ValueError` | If the target unit is not supported. |

#### `factor(by)`

Scale all force and moment values by a factor.

Parameters:

| Name | Type    | Description                                             | Default    |
| ---- | ------- | ------------------------------------------------------- | ---------- |
| `by` | `float` | Factor to scale by (can be positive, negative, or zero) | *required* |

Returns:

| Name      | Type      | Description                             |
| --------- | --------- | --------------------------------------- |
| `LoadSet` | `LoadSet` | New LoadSet instance with scaled values |

#### `to_ansys(folder_path='temp', name_stem=None, exclude=None)`

Export LoadSet to ANSYS load files.

Creates one file per load case with ANSYS F command format. Creates the output folder if it doesn't exist and cleans any existing files.

Parameters:

| Name          | Type        | Description | Default                                                               |
| ------------- | ----------- | ----------- | --------------------------------------------------------------------- |
| `folder_path` | \`str       | PathLike\`  | Directory to save the files. Defaults to 'temp'.                      |
| `name_stem`   | \`str       | None\`      | Optional base name for the files. If None, uses only load case names. |
| `exclude`     | \`list[str] | None\`      | List of point names to exclude from export.                           |

Raises:

| Type                | Description                                      |
| ------------------- | ------------------------------------------------ |
| `FileNotFoundError` | If the folder path exists but is not a directory |

#### `get_point_extremes(output=None)`

Get extreme values (max/min) for each point and component across all load cases.

Parameters:

| Name     | Type       | Description | Default                                                                           |
| -------- | ---------- | ----------- | --------------------------------------------------------------------------------- |
| `output` | \`PathLike | None\`      | Optional file path. If given, the extremes are also written as JSON to this file. |

Returns:

| Name   | Type   | Description                                                                                                                                                               |
| ------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `dict` | `dict` | Nested dictionary structure:: { "Point_A": { "fx": {"max": {"value": 100.0, "loadcase": "Case1"}, "min": {"value": 80.0, "loadcase": "Case2"}}, "fy": {...}, ... }, ... } |

#### `compare_to(other)`

Compare this LoadSet's envelope to another LoadSet's envelope.

Units are auto-converted if they differ (converts `other` to match `self`). For each shared point and component, a ComparisonRow is created for both the max and min extremes, with absolute and percentage differences.

Parameters:

| Name    | Type      | Description                     | Default    |
| ------- | --------- | ------------------------------- | ---------- |
| `other` | `LoadSet` | The LoadSet to compare against. | *required* |

Returns:

| Type             | Description                                        |
| ---------------- | -------------------------------------------------- |
| `LoadSetCompare` | A LoadSetCompare with detailed comparison results. |

Raises:

| Type         | Description                         |
| ------------ | ----------------------------------- |
| `ValueError` | If other is not a LoadSet instance. |

#### `envelope()`

Create an envelope LoadSet containing only load cases with extreme values.

For each point and component (fx, fy, fz, mx, my, mz), selects load cases with:

- Maximum value (always included)
- Minimum value (only if negative)

Load cases appearing multiple times (having extremes in multiple components) are deduplicated in the result.

Returns:

| Name      | Type      | Description                               |
| --------- | --------- | ----------------------------------------- |
| `LoadSet` | `LoadSet` | New LoadSet with envelope load cases only |

Raises:

| Type         | Description                  |
| ------------ | ---------------------------- |
| `ValueError` | If LoadSet has no load cases |

#### `print_head(n=5)`

Print a preview of the first N load cases as a formatted table.

Extreme values within each load case are highlighted (bold). Requires the `display` extra (`rich`).

Parameters:

| Name | Type  | Description                      | Default |
| ---- | ----- | -------------------------------- | ------- |
| `n`  | `int` | Number of load cases to display. | `5`     |

#### `print_table()`

Print all load cases as a formatted table.

Like `print_head` but shows every load case. Requires the `display` extra (`rich`).

#### `print_extremes()`

Print extreme values per point and component as a table.

Displays max/min values with their originating load case names. Requires the `display` extra (`rich`).

#### `envelope_to_markdown(output=None)`

Return the envelope summary as a Markdown table.

Generates a table with one max and one min row per point, showing all six components (fx–mz) and the originating load case.

Parameters:

| Name     | Type       | Description | Default                                   |
| -------- | ---------- | ----------- | ----------------------------------------- |
| `output` | \`PathLike | None\`      | Optional file path to write the Markdown. |

Returns:

| Type  | Description                                                       |
| ----- | ----------------------------------------------------------------- |
| `str` | The Markdown string (always returned, even when written to file). |

#### `print_envelope()`

Print envelope summary in wide format with one max and one min row per point.

Each row shows values for all 6 force/moment components. The max row shows the maximum value found across all load cases for each component independently, and the min row shows the minimum.

#### `read_ansys(file_path, units, name=None, version=1)`

Read a LoadSet from an ANSYS .inp file.

Parses ANSYS load files with the following format:

- /TITLE,{loadcase_name} - defines the load case name
- cmsel,s,pilot\_{node_name} - selects the pilot node
- f,all,{component},{value} - applies force/moment components

Parameters:

| Name        | Type       | Description                                       | Default                                                                |
| ----------- | ---------- | ------------------------------------------------- | ---------------------------------------------------------------------- |
| `file_path` | `PathLike` | Path to the ANSYS .inp file to read               | *required*                                                             |
| `units`     | `Units`    | Units to use for the LoadSet (forces and moments) | *required*                                                             |
| `name`      | \`str      | None\`                                            | Optional name for the LoadSet (defaults to filename without extension) |
| `version`   | `int`      | Version number for the LoadSet (defaults to 1)    | `1`                                                                    |

Returns:

| Name      | Type      | Description                                        |
| --------- | --------- | -------------------------------------------------- |
| `LoadSet` | `LoadSet` | The loaded LoadSet instance with a single LoadCase |

Raises:

| Type                | Description                                       |
| ------------------- | ------------------------------------------------- |
| `FileNotFoundError` | If the file doesn't exist                         |
| `ValueError`        | If the file format is invalid or cannot be parsed |

______________________________________________________________________

## LoadSetCompare

### `ductile_loads.LoadSetCompare`

LoadSetCompare contains the results of comparing two LoadSets. Provides tabular comparison data and export functionality.

#### `to_dict()`

Convert the comparison to a dictionary.

Returns:

| Type   | Description                                                                     |
| ------ | ------------------------------------------------------------------------------- |
| `dict` | A dict with two top-level keys:                                                 |
| `dict` | report_metadata.loadcases_info — contains loadset1 and loadset2 metadata dicts. |
| `dict` | comparisons — list of per-row dicts (one per point/component/type combination). |

#### `to_json(indent=2)`

Export LoadSetCompare to JSON string.

Parameters:

| Name     | Type  | Description            | Default |
| -------- | ----- | ---------------------- | ------- |
| `indent` | `int` | JSON indentation level | `2`     |

Returns:

| Name  | Type  | Description                           |
| ----- | ----- | ------------------------------------- |
| `str` | `str` | JSON representation of the comparison |

#### `new_exceeds_old()`

Check if loadset2 (new) exceeds loadset1 (old) envelope in any component comparison.

Returns True if at least one component comparison shows that loadset2 exceeds loadset1's bounds:

- For "max" type: loadset2_value > loadset1_value (higher maximum)
- For "min" type: loadset2_value < loadset1_value (lower minimum, more negative)

Returns:

| Name   | Type   | Description                                                                                                          |
| ------ | ------ | -------------------------------------------------------------------------------------------------------------------- |
| `bool` | `bool` | True if new loads exceed old envelope in at least one comparison, False if old loads fully envelope the new delivery |

#### `generate_comparison_report(output_dir, report_name='comparison_report', image_format='png', indent=2)`

Export complete comparison report including JSON data and chart images.

Creates a comprehensive report with:

- JSON file containing comparison data and generated chart filenames
- Chart image files for each point comparison

Parameters:

| Name           | Type       | Description                                                   | Default               |
| -------------- | ---------- | ------------------------------------------------------------- | --------------------- |
| `output_dir`   | `PathLike` | Directory to save the report files                            | *required*            |
| `report_name`  | `str`      | Base name for the report files (default: "comparison_report") | `'comparison_report'` |
| `image_format` | `str`      | Image format for charts (png, svg)                            | `'png'`               |
| `indent`       | `int`      | JSON indentation level                                        | `2`                   |

Returns:

| Name   | Type   | Description                            |
| ------ | ------ | -------------------------------------- |
| `Path` | `Path` | Path to the generated JSON report file |

Raises:

| Type                | Description                                            |
| ------------------- | ------------------------------------------------------ |
| `ImportError`       | If matplotlib is not available                         |
| `FileNotFoundError` | If output directory doesn't exist and can't be created |
| `ValueError`        | If report generation fails                             |

#### `generate_range_charts(output_dir=None, image_format='png', as_base64=False)`

Generate range bar chart images comparing LoadSets for each point.

Creates dual subplot charts showing force and moment ranges with bars representing the min-to-max range for each component.

Parameters:

| Name           | Type       | Description                                                    | Default                                                              |
| -------------- | ---------- | -------------------------------------------------------------- | -------------------------------------------------------------------- |
| `output_dir`   | \`PathLike | None\`                                                         | Directory to save the generated images (required if as_base64=False) |
| `image_format` | `str`      | Image format (png, svg)                                        | `'png'`                                                              |
| `as_base64`    | `bool`     | If True, return base64-encoded strings instead of saving files | `False`                                                              |

Returns:

| Name   | Type              | Description |
| ------ | ----------------- | ----------- |
| `dict` | \`dict\[str, Path | str\]\`     |

Raises:

| Type                | Description                                                                   |
| ------------------- | ----------------------------------------------------------------------------- |
| `ImportError`       | If matplotlib is not available                                                |
| `FileNotFoundError` | If output directory doesn't exist and can't be created (when as_base64=False) |
| `ValueError`        | If output_dir is None and as_base64=False                                     |

### `ductile_loads.ComparisonRow`

ComparisonRow represents one row in a LoadSet comparison table. Each row compares a specific point/component/type combination between two LoadSets.
