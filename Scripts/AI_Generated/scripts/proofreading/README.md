# Proofreading Scripts

Scripts that support distributed proofreading workflows by splitting large YAML files
into smaller chunks and managing review fields.

## Scripts

### splitYamlForProofreading.py
Splits large YAML files into multiple smaller files for distributed proofreading.

**Usage:**
```bash
python3 Scripts/AI_Generated/scripts/proofreading/splitYamlForProofreading.py
```

**Functionality:**
1. Reads `multiple_dhatu_ids.yaml` (285 entries) and splits into 10 files (~28-29 entries each)
2. Reads `not_found_dhatu_ids_without_gati.yaml` (595 entries) and splits into 10 files (~59-60 entries each)
3. Creates folders:
   - `Scripts/output/multiple_dhatu_ids/`
   - `Scripts/AI_Generated/output/not_found_dhatu_ids_without_gati/`
4. Creates files named: `part_01.yaml`, `part_02.yaml`, ..., `part_10.yaml` in each folder

---

### addReviewFields.py
Adds 'resolved' and 'comment' fields to all entries in split files for proofreading workflow.

**Usage:**
```bash
python3 Scripts/AI_Generated/scripts/proofreading/addReviewFields.py
```

**Functionality:**
1. Adds `resolved: false` to each entry
2. Adds `comment: ""` to each entry
3. These fields are for proofreading workflow only (not backported to Data/)

**Note:** These review fields help track proofreading progress but are not propagated
back to the original YAML files in the Data/ folder.

---

### removeResolvedEntries.py
Removes entries marked as `resolved=true` from split files after proofreading.

**Usage:**
```bash
python3 Scripts/AI_Generated/scripts/proofreading/removeResolvedEntries.py
```

**Functionality:**
1. Reads all `part_*.yaml` files in the folders
2. Removes entries where `resolved=true`
3. Keeps entries where `resolved=false`
4. Updates the files and entry counts
5. Reports statistics on removed entries

---

## Proofreading Workflow

1. **Split** large files into manageable chunks using `splitYamlForProofreading.py`
2. **Add Review Fields** using `addReviewFields.py` to track progress
3. **Distribute** the `part_*.yaml` files to proofreaders
4. **Review** each entry, marking `resolved: true` when corrected and adding comments
5. **Remove Resolved** entries using `removeResolvedEntries.py`
6. **Backport** corrected entries using the backport scripts

This workflow allows multiple people to work on different parts of the correction
process simultaneously.
