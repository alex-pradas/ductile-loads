# Input/Output Formats

## JSON input

`LoadSet.read_json()` expects a JSON file matching the Pydantic schema:

```
{
  "name": "Supplier Forces v1",
  "version": 1,
  "units": {"forces": "N", "moments": "Nm"},
  "loads_type": "limit",
  "load_cases": [
    {
      "name": "Case_A",
      "description": "Full braking at 120 km/h",
      "point_loads": [
        {
          "name": "left_mount",
          "force_moment": {
            "fx": 100.0,
            "fy": -50.0,
            "fz": 0.0,
            "mx": 0.0,
            "my": 0.0,
            "mz": 0.0
          }
        }
      ]
    }
  ]
}
```

### Required fields

- `name` — load set identifier (string or null)
- `version` — integer version number
- `units` — object with `forces` and `moments` keys
- `load_cases` — array of load case objects

### Optional fields

- `description` — free-text description
- `loads_type` — `"limit"` or `"ultimate"` (or null)

You can generate the full JSON Schema programmatically:

```
from ductile_loads import LoadSet

schema = LoadSet.generate_json_schema(output_file="loadset_schema.json")
```

## ANSYS output (.inp)

`to_ansys()` generates one `.inp` file per load case. Each file contains ANSYS APDL commands:

```
/TITLE,Case_A
nsel,u,,,all

cmsel,s,pilot_left_mount
f,all,fx,1.000e+02
f,all,fy,-5.000e+01
nsel,u,,,all


alls
```

### Format details

- `/TITLE,{loadcase_name}` — sets the load case name
- `cmsel,s,pilot_{point_name}` — selects the pilot node for a point
- `f,all,{component},{value}` — applies a force or moment component
- Only non-zero components are written
- Component order: fx, fy, mx, my, mz, fz
- Point names are automatically prefixed with `pilot_`
- Values are formatted in scientific notation (3 decimal places)

### Reading ANSYS files

To read an existing `.inp` file back into a `LoadSet`:

```
from ductile_loads import LoadSet, Units

ls = LoadSet.read_ansys(
    "design_load_01.inp",
    units=Units(forces="N", moments="Nm"),
    name="Imported loads",
)
```

## Markdown output

`envelope_to_markdown()` generates a Markdown table:

```
## Supplier Forces v1 — Envelope Summary

Version: 1 | Units: N, Nm

| Point | Type | FX | FY | FZ | MX | MY | MZ |
|-------|------|-------:|-------:|-------:|-------:|-------:|-------:|
| left_mount | max | 100.0 | 0.000 | 50.0 | 0.000 | 0.000 | 0.000 |
| | min | -20.0 | -50.0 | 0.000 | 0.000 | 0.000 | 0.000 |

Points: 1 | From 5 load cases
```

## JSON extremes output

`get_point_extremes()` returns (and optionally writes) a nested dictionary:

```
{
  "left_mount": {
    "fx": {
      "max": {"value": 100.0, "loadcase": "Case_A"},
      "min": {"value": -20.0, "loadcase": "Case_C"}
    },
    "fy": {
      "max": {"value": 0.0, "loadcase": "Case_A"},
      "min": {"value": -50.0, "loadcase": "Case_A"}
    }
  }
}
```

Components where both max and min are zero are filtered out.
