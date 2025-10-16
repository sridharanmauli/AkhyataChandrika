# Test Scripts

Automated test suites that verify the functionality of collection, backport, and proofreading workflows.

## Scripts

### testBackportIntegrity.py
Tests the backport functionality to ensure changes are correctly applied to original YAML files.

**Usage:**
```bash
python3 Scripts/AI_Generated/tests/testBackportIntegrity.py
```

**Tests:**
- Backport operations preserve YAML structure
- dhatu_id updates are correctly applied
- No data loss during backport
- File formatting is maintained

---

### testCompleteBackportWorkflow.py
Comprehensive test suite that validates the entire workflow from collection to backport.

**Usage:**
```bash
python3 Scripts/AI_Generated/tests/testCompleteBackportWorkflow.py
```

**Tests:**
- Collection scripts correctly identify problematic entries
- YAML files are properly formatted
- Backport scripts correctly update original files
- End-to-end workflow integrity
- Edge cases and error handling

---

### testReviewWorkflow.py
Tests the proofreading workflow including split, review fields, and resolved entry removal.

**Usage:**
```bash
python3 Scripts/AI_Generated/tests/testReviewWorkflow.py
```

**Tests:**
- Splitting creates correct number of files
- Review fields are properly added
- Resolved entries are correctly removed
- Entry counts are accurate
- Split files can be merged back correctly

---

## Running Tests

Run all tests:
```bash
cd Scripts/AI_Generated/tests
python3 testBackportIntegrity.py
python3 testCompleteBackportWorkflow.py
python3 testReviewWorkflow.py
```

Or run individual tests as needed.

## Test Status

All tests should pass with 100% success rate. If any tests fail, review the
error messages and ensure the workflow scripts are functioning correctly.
