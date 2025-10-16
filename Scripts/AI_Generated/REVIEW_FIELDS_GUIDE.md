## Review Fields Guide

## Overview

Each entry in the proofreading files now has two additional fields for tracking review progress:
- **`resolved`**: Set to `true` when proofreading is complete for that entry
- **`comment`**: Add notes, issues, or questions about the entry

These fields are **only for the proofreading workflow** and are **not backported** to the Data folder.

## Entry Format

```yaml
"फलति":
  "form": "फलति"
  "dhatu_ids": "01.0594, 01.0608"     # ← Edit this (select correct ID)
  "gati": ""
  "kanda": "प्रथमकाण्डः"
  "varga": "भावविकारवर्गः"
  "adhikaar": ""
  "artha": "विशरणे"
  "shloka_num": "13"
  "shloka_text": "जूर्यते जारयति च..."
  "resolved": "false"                  # ← Set to "true" when done
  "comment": ""                        # ← Add notes here
```

## Proofreading Workflow

### Step 1: Review an Entry

1. Look at the `dhatu_ids` or `dhatu_id` field
2. Find the correct value
3. Update the field with the correct value
4. Set `resolved: "true"`
5. Optionally add a comment

**Example - Before:**
```yaml
"फलति":
  "dhatu_ids": "01.0594, 01.0608"
  "resolved": "false"
  "comment": ""
```

**Example - After:**
```yaml
"फलति":
  "dhatu_ids": "01.0594"               # ← Selected correct ID
  "resolved": "true"                   # ← Marked as done
  "comment": "Verified in Panini 1.594"  # ← Added reference
```

### Step 2: Using Comments

Comments are useful for:
- Recording your research/reasoning
- Noting uncertainties or questions
- Marking entries that need second review
- Leaving notes for other proofreaders

**Examples:**
```yaml
"comment": "Confirmed with Prof. Sharma"
"comment": "Unsure between these two - needs review"
"comment": "TODO: Check cross-reference in shloka 45"
"comment": "Same as entry in part_03.yaml"
```

### Step 3: Track Progress

Each file header shows the total entries:
```yaml
# ENTRIES TO CORRECT: 60
```

You can track your progress by:
- Counting how many entries have `resolved: "true"`
- Using comments to mark "in progress" vs "done"
- Leaving unresolved entries as `resolved: "false"`

## Cleanup After Review

### Remove Resolved Entries

After completing proofreading, remove all resolved entries from the files:

**Dry run (preview what will be removed):**
```bash
python3 Scripts/AI_Generated/scripts/removeResolvedEntries.py --dry-run
```

**Actually remove:**
```bash
python3 Scripts/AI_Generated/scripts/removeResolvedEntries.py
```

This will:
- Remove all entries where `resolved: "true"`
- Keep all entries where `resolved: "false"`
- Update the entry counts in file headers
- Show detailed statistics

**Example output:**
```
Processing: multipleDhatuIdsWithoutGati
  📝 part_01.yaml:
     Before: 16 entries
     After:  10 entries
     Removed: 6 resolved entries
     ✅ File updated
```

## Backporting

The `resolved` and `comment` fields are **automatically ignored** during backporting:

```bash
# These commands ignore resolved/comment fields
python3 Scripts/AI_Generated/scripts/backportMultipleDhatuIds.py \
    Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati \
    Data

python3 Scripts/AI_Generated/scripts/backportNotFoundDhatuIds.py \
    Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati \
    Data
```

Only the `dhatu_id` or `dhatu_ids` changes are backported to the Data folder.

## Complete Workflow Example

### Day 1: Start Proofreading
```yaml
# part_05.yaml - Person 5's assignment
# ENTRIES TO CORRECT: 60

"स्वीकरोति":
  "dhatu_id": "Not Found"
  "resolved": "false"
  "comment": ""
```

### Day 2: Research and Update
```yaml
"स्वीकरोति":
  "dhatu_id": "01.1234"              # ← Found correct ID
  "resolved": "true"                 # ← Marked complete
  "comment": "Found in reference book pg 45"
```

### Day 3: Continue with Next Entries
```yaml
"स्वीकुरुते":
  "dhatu_id": "01.1234"
  "resolved": "true"
  "comment": "Same root as स्वीकरोति"

"प्रतीच्छति":
  "dhatu_id": "Not Found"
  "resolved": "false"
  "comment": "TODO: Check tomorrow"  # ← In progress
```

### Day 4: Finish and Clean Up
When all 60 entries are done:
```bash
# Remove resolved entries
python3 Scripts/AI_Generated/scripts/removeResolvedEntries.py

# Now part_05.yaml only has unresolved entries (if any)
# Or is much smaller if most were resolved
```

### Day 5: Backport Changes
After all proofreaders finish:
```bash
# Backport all changes to Data folder
python3 Scripts/AI_Generated/scripts/backportNotFoundDhatuIds.py \
    Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati \
    Data
```

## Tips for Proofreaders

### ✅ Good Practices

1. **Set resolved immediately** when done with an entry
2. **Use comments** to document your reasoning
3. **Be specific** in comments (include page numbers, references, etc.)
4. **Ask for help** using comments (e.g., "Need second opinion")
5. **Save frequently** while editing YAML files

### ❌ Things to Avoid

1. **Don't remove entries manually** - use the cleanup script
2. **Don't modify other fields** besides `dhatu_id(s)`, `resolved`, and `comment`
3. **Don't mark as resolved** if uncertain - use comment instead
4. **Don't break YAML syntax** - be careful with quotes and indentation

### 🔍 Checking Your Progress

Count resolved entries in a file:
```bash
grep -c 'resolved": "true"' part_05.yaml
```

List all comments:
```bash
grep 'comment":' part_05.yaml | grep -v 'comment": ""'
```

## Scripts Reference

### Add Review Fields (Already Done)
```bash
python3 Scripts/AI_Generated/scripts/addReviewFields.py
```
Adds `resolved` and `comment` fields to all entries.

### Remove Resolved Entries
```bash
# Preview
python3 Scripts/AI_Generated/scripts/removeResolvedEntries.py --dry-run

# Execute
python3 Scripts/AI_Generated/scripts/removeResolvedEntries.py
```

### Test Review Workflow
```bash
python3 Scripts/AI_Generated/scripts/testReviewWorkflow.py
```
Runs automated tests to verify the review workflow works correctly.

## FAQs

**Q: What happens if I don't set resolved to true?**
A: The entry stays in the file for future review. Only entries with `resolved: "true"` are removed.

**Q: Can I set resolved=true without editing the dhatu_id?**
A: Yes, but this means "I reviewed it and it's correct as-is" or "I can't fix this." Use a comment to clarify.

**Q: Will comments be saved to the Data folder?**
A: No, comments are only for the proofreading workflow and are not backported.

**Q: Can I undo removeResolvedEntries.py?**
A: Once removed, resolved entries are deleted. Make sure you've backported changes first, or keep backups.

**Q: How do I handle difficult entries?**
A: Leave `resolved: "false"` and add a detailed comment explaining the issue. Another proofreader can review it later.

**Q: Can multiple people work on the same file?**
A: Not recommended - each person should have their own part_XX.yaml files to avoid conflicts.

---

**Last Updated:** 2025-10-17
**Status:** ✅ Fully tested and working
