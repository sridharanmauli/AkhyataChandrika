#!/usr/bin/env python3
"""
Fix YAML indentation in बुद्धिवर्गः file.

The correct structure should match other vargas:
"sloka...": null
category:
  - verb:
  - verb2:

Issues to fix:
1. Categories should be unquoted
2. Verbs should end with ":"
3. Verbs should have proper spacing after "-"
"""

import re

def fix_buddhivarga_yaml(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    fixed_lines = []

    for line in lines:
        # Skip empty lines
        if line.strip() == '':
            fixed_lines.append(line)
            continue

        # Sloka lines - keep as is (they should end with ": null")
        if re.match(r'^"[^"]+":\s*null?\s*$', line):
            # Ensure it has null at the end
            if not line.strip().endswith('null'):
                fixed_lines.append(line.rstrip() + ' null')
            else:
                fixed_lines.append(line)
            continue

        # Quoted category lines - unquote them
        # Pattern: "category": or "category":
        match = re.match(r'^"([^"]+)":(\s*)$', line)
        if match:
            category = match.group(1)
            # Unquote and keep at 0 indentation
            fixed_lines.append(f'{category}:')
            continue

        # Unquoted category lines - keep as is
        if re.match(r'^[^\s"][^:]*:(\s*)$', line) and not line.strip().startswith('-'):
            fixed_lines.append(line)
            continue

        # Verb lines - fix spacing and ensure they end with ":"
        # Patterns to match:
        # - "  - verb:" (correct)
        # - "  - verb" (missing colon)
        # - "  -verb:" (missing space)
        # - "  -verb" (missing space and colon)
        verb_match = re.match(r'^(\s*)-\s*([^:]+):?\s*$', line)
        if verb_match:
            indent = verb_match.group(1)
            verb = verb_match.group(2).strip()
            # Ensure proper indentation (2 spaces) and format
            fixed_lines.append(f'  - {verb}:')
            continue

        # Any other line - keep as is
        fixed_lines.append(line)

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))

    print(f"✓ Fixed बुद्धिवर्गः YAML written to {output_file}")

if __name__ == "__main__":
    input_file = "../Data/1_प्रथमकाण्डः/2_बुद्धिवर्गः.yaml"
    output_file = "../Data/1_प्रथमकाण्डः/2_बुद्धिवर्गः.yaml"
    fix_buddhivarga_yaml(input_file, output_file)
