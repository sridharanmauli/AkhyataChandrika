#!/usr/bin/env python3
"""
Fix YAML indentation in भावविकारवर्गः file.
The issue is that verbs under categories are formatted as list items when they should be mapping keys.

The correct structure should be:
"sloka...":
  "category":
    "verb":
      - "ref1"
      - "ref2"
    "verb2": null

Instead of:
"sloka...":
  "category":
  - "verb":
    - "ref1"
    - "ref2"
  - "verb2": null
"""

import re

def fix_yaml_indentation(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    fixed_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Sloka line (level 0): starts with " and ends with :
        if re.match(r'^"[^"]+":\s*$', line):
            fixed_lines.append(line)
            i += 1
            continue

        # Category line (level 1): 2 spaces + "category":
        if re.match(r'^  "[^"]+":$', line):
            fixed_lines.append(line)
            i += 1

            # Process all verbs under this category
            while i < len(lines):
                verb_line = lines[i]

                # Check if this is a verb line formatted as list item
                # Pattern: 2 spaces + - + "verb":
                verb_match = re.match(r'^  - ("[^"]+":)\s*$', verb_line)
                if verb_match:
                    # Convert to proper mapping: 4 spaces + "verb":
                    fixed_lines.append('    ' + verb_match.group(1))
                    i += 1

                    # Process values under this verb
                    while i < len(lines):
                        value_line = lines[i]

                        # Value list item: 4 spaces + - + value
                        if re.match(r'^    - ', value_line):
                            # Add 2 more spaces: 6 spaces + - + value
                            fixed_lines.append('  ' + value_line)
                            i += 1
                        else:
                            # Not a value, break to process next verb
                            break
                    continue

                # Check if it's a verb with inline null
                # Pattern: 2 spaces + - + "verb": null
                verb_null_match = re.match(r'^  - ("[^"]+": null)\s*$', verb_line)
                if verb_null_match:
                    # Convert to proper mapping: 4 spaces + "verb": null
                    fixed_lines.append('    ' + verb_null_match.group(1))
                    i += 1
                    continue

                # If it's another category or sloka, break out
                if (re.match(r'^  "[^"]+":$', verb_line) or
                    re.match(r'^"[^"]+":', verb_line)):
                    break

                # Skip empty lines or add as-is
                if verb_line.strip() == '':
                    fixed_lines.append(verb_line)
                    i += 1
                else:
                    # Unknown pattern, keep as-is
                    fixed_lines.append(verb_line)
                    i += 1
                    break
            continue

        # Any other line, keep as-is
        fixed_lines.append(line)
        i += 1

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))

    print(f"✓ Fixed YAML written to {output_file}")

if __name__ == "__main__":
    input_file = "../Data/1_प्रथमकाण्डः/1_भावविकारवर्गः.yaml"
    output_file = "../Data/1_प्रथमकाण्डः/1_भावविकारवर्गः.yaml"
    fix_yaml_indentation(input_file, output_file)
