# Distributed Proofreading Workflow

This document explains the workflow for distributing proofreading tasks among multiple people and backporting their changes.

## Overview

The YAML files containing dhatu_id issues have been split into folders with 10 parts each, allowing 10 people to proofread in parallel.

## File Structure

### Multiple Dhatu IDs Without Gati (159 entries total)
**Location:** `Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati/`
- `part_01.yaml` - `part_10.yaml` (16 entries each, except part_10 with 15)
- Each file contains verbs (without gati) that have multiple dhatu_ids
- Proofreaders need to select the correct dhatu_id for each entry

### Not Found Dhatu IDs Without Gati (595 entries total)
**Location:** `Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati/`
- `part_01.yaml` - `part_10.yaml` (60 entries each, except part_10 with 55)
- Each file contains verbs (without gati) with "Not Found" dhatu_id
- Proofreaders need to find and assign the correct dhatu_id

## Workflow

### Step 1: Split Files (Already Done)
```bash
python3 Scripts/AI_Generated/scripts/splitYamlForProofreading.py
```

This creates:
- 10 files in `Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati/`
- 10 files in `Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati/`

### Step 2: Distribute to Proofreaders

Assign files to 10 proofreaders:
- **Person 1:** `part_01.yaml` from both folders
- **Person 2:** `part_02.yaml` from both folders
- **Person 3:** `part_03.yaml` from both folders
- ... and so on

Each person will have approximately:
- 16 multiple dhatu_id entries to resolve (without gati)
- 60 not found dhatu_id entries to find (without gati)

### Step 3: Proofreading Instructions

#### For Multiple Dhatu IDs files:
Edit the `dhatu_ids` field to keep only the correct dhatu_id.

Example - Before:
```yaml
"फलति":
  "form": "फलति"
  "dhatu_ids": "01.0594, 01.0608"
  "gati": ""
  ...
```

After (selecting the correct one):
```yaml
"फलति":
  "form": "फलति"
  "dhatu_ids": "01.0594"
  "gati": ""
  ...
```

#### For Not Found Dhatu IDs files:
Change `dhatu_id` from "Not Found" to the correct ID.

Example - Before:
```yaml
"सिद्ध्यति":
  "form": "सिद्ध्यति"
  "dhatu_id": "Not Found"
  "gati": ""
  ...
```

After:
```yaml
"सिद्ध्यति":
  "form": "सिद्ध्यति"
  "dhatu_id": "04.0087"
  "gati": ""
  ...
```

### Step 4: Backport Changes

After all proofreaders finish, backport the changes to the original YAML files in the `Data/` folder.

#### Backport Multiple Dhatu IDs:
```bash
python3 Scripts/AI_Generated/scripts/backportMultipleDhatuIds.py \
    Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati \
    Data
```

#### Backport Not Found Dhatu IDs:
```bash
python3 Scripts/AI_Generated/scripts/backportNotFoundDhatuIds.py \
    Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati \
    Data
```

The backport scripts will:
- Process all `part_*.yaml` files in the folder
- Find the corresponding entries in the original YAML files
- Update the dhatu_id values
- Report all changes made

## Important Notes

1. **Don't modify other fields**: Only edit the `dhatu_ids` or `dhatu_id` field. Keep all other fields unchanged.

2. **Maintain YAML format**: Be careful not to break the YAML structure while editing.

3. **Partial backports allowed**: The backport script can be run multiple times. It will only update entries that have been edited (i.e., entries where "Not Found" has been replaced).

4. **Backward compatible**: The backport scripts still support the old single-file format for backward compatibility.

## Scripts Reference

- **Split Script:** `Scripts/AI_Generated/scripts/splitYamlForProofreading.py`
  - Splits both files into 10 parts each
  - Creates folders with part_01.yaml through part_10.yaml

- **Backport Scripts:**
  - `Scripts/AI_Generated/scripts/backportMultipleDhatuIds.py`
  - `Scripts/AI_Generated/scripts/backportNotFoundDhatuIds.py`
  - Both scripts now support folder input with multiple files

## Re-splitting (if needed)

If you need to re-split the files (e.g., after backporting some changes), simply run the split script again. It will overwrite the existing split files with fresh data from the source files.
