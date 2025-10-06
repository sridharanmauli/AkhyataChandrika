## Request: generate_yaml from parsed_dict.generated.json

- Input: `Scripts/dictionary/out/parsed_dict.generated.json`
- `text_number` format: `x.y.z` where x = खण्ड (khanda), y = वर्ग (varga), z = item index
- No deduplication or merging; write entries as-is
- Output root: `generated/`

Valid `x.y.z`:
- Directory: `generated/x/`
- File: `generated/x/y.yaml`
- In each `y.yaml`, append entries in the same order as in the input (no sorting)
- Do not reorder existing file contents; just append new entries
- Entry format:

```yaml
artha:
  - synonym1:
  - synonym2:
```

Invalid `text_number` (missing/malformed/non-integer parts):
- Write full items to `generated/invalid/invalid.text_numbers.json` (JSON lines or array)
- Also append to `generated/invalid/invalid.text_numbers.yaml` using the same YAML format as valid entries


