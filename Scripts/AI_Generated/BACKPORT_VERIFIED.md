# Backport Workflow - Verified and Working ✅

## Overview

The backport workflow has been **fully tested and verified** to work correctly. Changes made to split files in the folders will properly backport to the Data folder.

## Verified Flow

```
Edit Split Files → Run Backport Script → Changes Applied to Data Folder ✅
```

## Test Results

### ✅ Test 1: Multiple Dhatu IDs Backport
- **Source:** `Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati/part_01.yaml`
- **Action:** Changed `dhatu_ids` from "01.0594, 01.0608" to "01.0594"
- **Target:** `Data/1_प्रथमकाण्डः/1_भावविकारवर्गः.yaml`
- **Result:** ✅ **PASSED** - Change successfully appeared in Data folder

### ✅ Test 2: Not Found Dhatu IDs Backport
- **Source:** `Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati/part_01.yaml`
- **Action:** Changed `dhatu_id` from "Not Found" to "99.9999"
- **Target:** `Data/1_प्रथमकाण्डः/1_भावविकारवर्गः.yaml`
- **Result:** ✅ **PASSED** - Change successfully appeared in Data folder

## How It Works

### 1. Proofreader Edits Files

**For Multiple Dhatu IDs (`multipleDhatuIdsWithoutGati/`):**
```yaml
# Before editing
"फलति":
  "dhatu_ids": "01.0594, 01.0608"

# After selecting correct one
"फलति":
  "dhatu_ids": "01.0594"
```

**For Not Found Dhatu IDs (`notFoundDhatuIdsWithoutGati/`):**
```yaml
# Before editing
"सिद्ध्यति":
  "dhatu_id": "Not Found"

# After finding correct ID
"सिद्ध्यति":
  "dhatu_id": "04.0087"
```

### 2. Run Backport Scripts

After all proofreading is complete:

**Backport Multiple Dhatu IDs:**
```bash
python3 Scripts/AI_Generated/scripts/backportMultipleDhatuIds.py \
    Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati \
    Data
```

**Backport Not Found Dhatu IDs:**
```bash
python3 Scripts/AI_Generated/scripts/backportNotFoundDhatuIds.py \
    Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati \
    Data
```

### 3. Changes Automatically Applied to Data Folder

The backport script:
1. Reads all `part_*.yaml` files from the folder
2. For each entry, finds the corresponding location in the Data folder
3. Updates the `dhatu_id` or `dhatu_ids` field
4. Saves the updated Data files
5. Reports all changes made

## File Mapping

The backport script automatically maps entries to the correct Data files:

```
Split File Entry                    →  Data File
─────────────────────────────────────────────────────────────
kanda: "प्रथमकाण्डः"                →  Data/1_प्रथमकाण्डः/
varga: "भावविकारवर्गः"              →  1_भावविकारवर्गः.yaml
adhikaar: "भ्वादिगणः" (if present) →  subfolder/1_भ्वादिगणः.yaml
```

## Verification

To re-verify the backport workflow anytime:

```bash
python3 Scripts/AI_Generated/scripts/testCompleteBackportWorkflow.py
```

This test:
- Makes temporary edits to split files
- Runs backport scripts
- Verifies changes appear in Data folder
- Restores everything to original state
- Reports pass/fail for each test

## Important Notes

### ✅ Confirmed Working
- Backport from `multipleDhatuIdsWithoutGati/` to `Data/` ✅
- Backport from `notFoundDhatuIdsWithoutGati/` to `Data/` ✅
- All entry metadata (kanda, varga, adhikaar) correctly mapped ✅
- Proper YAML formatting preserved ✅

### 🔄 Workflow Support
- Can backport individual files or entire folders ✅
- Can run backport multiple times (idempotent) ✅
- Skips entries that haven't been edited yet ✅
- Reports all changes made ✅

### 📝 What Gets Updated in Data Folder

**For Multiple Dhatu IDs:**
- Updates the array in Data file from `[gati, "id1, id2"]` to `[gati, "selected_id"]`
- Or from `["id1, id2"]` to `["selected_id"]` (without gati)

**For Not Found Dhatu IDs:**
- Updates the array in Data file from `null` to `["new_id"]`
- Or from `null` to `[gati, "new_id"]` (with gati)

## Example: Complete Workflow

### Step 1: Distribute Files
Give each proofreader their assigned `part_XX.yaml` files from both folders.

### Step 2: Proofreading
Proofreaders edit their files:
- Person 1 edits: `part_01.yaml` from both folders
- Person 2 edits: `part_02.yaml` from both folders
- ... and so on

### Step 3: Collect Edited Files
Gather all edited `part_*.yaml` files back into their respective folders.

### Step 4: Backport
Run both backport commands:
```bash
# Backport multiple dhatu IDs
python3 Scripts/AI_Generated/scripts/backportMultipleDhatuIds.py \
    Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati \
    Data

# Backport not found dhatu IDs
python3 Scripts/AI_Generated/scripts/backportNotFoundDhatuIds.py \
    Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati \
    Data
```

### Step 5: Verify
Check the backport output for:
- ✅ Number of entries processed
- ✅ Number successfully updated
- ✅ List of modified Data files

### Step 6: Commit Changes
If everything looks good, commit the updated Data files to git.

## Safety Features

1. **No data loss:** Original Data files are only updated, never deleted
2. **Selective updates:** Only edited entries are backported
3. **Idempotent:** Can run backport multiple times safely
4. **Detailed logging:** Every change is reported
5. **Validation:** Entry metadata must match to backport

## Troubleshooting

### If backport reports "not found"
- Check that kanda/varga/adhikaar names match exactly
- Verify the shloka_text matches
- Ensure the verb form exists in the Data file

### If changes don't appear
- Check the backport output for errors
- Verify you're editing the correct field (`dhatu_id` vs `dhatu_ids`)
- Run the test script to verify backport is working

### If you need help
- Run: `python3 Scripts/AI_Generated/scripts/testCompleteBackportWorkflow.py`
- Check: `Scripts/AI_Generated/PROOFREADING_WORKFLOW.md`
- Review: Backport script output for detailed error messages

---

**Last Verified:** 2025-10-17
**Status:** ✅ All tests passing
**Test Script:** `Scripts/AI_Generated/scripts/testCompleteBackportWorkflow.py`
