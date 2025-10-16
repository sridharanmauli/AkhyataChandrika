# Backport Scripts

Scripts that apply manually edited changes from YAML files back to the original Data/ folder YAML files.

## Scripts

### backportMultipleDhatuIds.py
Backports manually edited dhatu_id changes from the multiple_dhatu_ids YAML files
back to the original YAML files in the Data folder.

**Usage:**
```bash
# Process all files in output directory:
python3 Scripts/AI_Generated/scripts/backport/backportMultipleDhatuIds.py \
    Scripts/AI_Generated/output \
    Data

# Or process a single file:
python3 Scripts/AI_Generated/scripts/backport/backportMultipleDhatuIds.py \
    Scripts/AI_Generated/output/multiple_dhatu_ids_without_gati.yaml \
    Data
```

**Functionality:**
1. Reads the manually edited YAML file(s)
2. Finds the corresponding entries in original YAML files
3. Updates the dhatu_id field
4. Preserves all other fields and formatting

---

### backportNotFoundDhatuIds.py
Backports manually edited dhatu_id changes from the not_found_dhatu_ids YAML files
back to the original YAML files in the Data folder.

**Usage:**
```bash
# Process all files in output directory:
python3 Scripts/AI_Generated/scripts/backport/backportNotFoundDhatuIds.py \
    Scripts/AI_Generated/output \
    Data

# Or process a single file:
python3 Scripts/AI_Generated/scripts/backport/backportNotFoundDhatuIds.py \
    Scripts/AI_Generated/output/not_found_dhatu_ids_without_gati.yaml \
    Data
```

**Functionality:**
1. Reads the manually edited YAML file(s) where "Not Found" has been replaced
2. Finds the corresponding entries in original YAML files
3. Updates the dhatu_id field with the newly assigned value
4. Skips entries still marked as "Not Found"

---

## Important Notes

- Always backup your Data/ folder before running backport scripts
- The scripts preserve YAML structure and formatting
- You can process individual files or entire directories
- Backport scripts report statistics on changes made
