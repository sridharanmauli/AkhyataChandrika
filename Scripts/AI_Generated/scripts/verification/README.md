# Verification Scripts

Scripts that verify data integrity and validate workflows.

## Scripts

### verifySplitIntegrity.py
Verifies that splitting YAML files into parts doesn't lose or corrupt data.

**Usage:**
```bash
python3 Scripts/AI_Generated/scripts/verification/verifySplitIntegrity.py
```

**Functionality:**
1. Compares original YAML files with split parts
2. Verifies all entries are preserved
3. Checks for data corruption or loss
4. Reports any discrepancies

---

### verifyResolvedDeletionAndBackport.py
Comprehensive verification script that validates the complete proofreading and backport workflow.

**Usage:**
```bash
python3 Scripts/AI_Generated/scripts/verification/verifyResolvedDeletionAndBackport.py
```

**Functionality:**
1. Verifies resolved entries are correctly removed from split files
2. Validates backport operations
3. Ensures data consistency between split files and original YAML
4. Reports detailed statistics and any issues

---

### addEntryCountsToHeaders.py
Adds entry count metadata to YAML file headers for easy tracking.

**Usage:**
```bash
python3 Scripts/AI_Generated/scripts/verification/addEntryCountsToHeaders.py
```

**Functionality:**
1. Counts entries in YAML files
2. Adds/updates entry count in file headers
3. Useful for quickly seeing how many entries remain to be processed

---

## Best Practices

- Run verification scripts after major operations (split, backport)
- Use `addEntryCountsToHeaders.py` to track progress
- Verify integrity before and after manual edits
- Keep verification logs for audit trails
