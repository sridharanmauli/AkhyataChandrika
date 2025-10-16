#!/usr/bin/env python3
"""
Fix YAML indentation issue where artha categories are not properly nested under shloka text.

The issue: YAML files in Data directory have structure like:
  "shloka text...॥":
  artha:           ← should be indented!
    - verb1:
    - verb2:

This script indents all artha lines (non-shloka, non-list lines with colons)
so they become children of the previous shloka.
"""

import os
import sys
import glob

def fix_yaml_indentation(file_path, dry_run=False):
    """
    Fix indentation in a YAML file.

    Args:
        file_path: Path to the YAML file
        dry_run: If True, don't write changes, just report what would be done

    Returns:
        Number of lines that were indented
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed_lines = []
    indented_count = 0

    for i, line in enumerate(lines):
        stripped = line.lstrip()
        leading_spaces = len(line) - len(stripped)

        # Check if this is a shloka line (ends with ॥":)
        if line.strip().endswith('॥":'):
            fixed_lines.append(line)
        # Check if this is an artha line that should be indented:
        # - No leading spaces (column 0)
        # - Not a list item (doesn't start with -)
        # - Not a quoted string (doesn't start with ")
        # - Has a colon (is a key)
        elif (leading_spaces == 0 and
              not stripped.startswith('-') and
              not stripped.startswith('"') and
              ':' in stripped):
            # Indent this line by 2 spaces
            fixed_lines.append('  ' + line)
            indented_count += 1
        else:
            fixed_lines.append(line)

    # Write changes if not dry run
    if not dry_run and indented_count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)

    return indented_count

def fix_all_yaml_files(data_dir, dry_run=False):
    """
    Fix all YAML files in the Data directory.

    Args:
        data_dir: Path to the Data directory
        dry_run: If True, don't write changes, just report
    """
    # Find all YAML files recursively
    yaml_files = glob.glob(os.path.join(data_dir, '**/*.yaml'), recursive=True)

    print(f"Found {len(yaml_files)} YAML files")
    if dry_run:
        print("DRY RUN - no files will be modified\n")
    print()

    total_indented = 0
    files_modified = 0

    for yaml_file in yaml_files:
        rel_path = os.path.relpath(yaml_file, data_dir)
        indented = fix_yaml_indentation(yaml_file, dry_run=dry_run)

        if indented > 0:
            status = "[DRY RUN] Would indent" if dry_run else "Indented"
            print(f"{status} {indented} lines in: {rel_path}")
            files_modified += 1
            total_indented += indented

    print()
    print(f"Summary:")
    print(f"  Files modified: {files_modified}/{len(yaml_files)}")
    print(f"  Total lines indented: {total_indented}")

    if dry_run:
        print("\nRun without --dry-run to apply changes")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fix YAML indentation in Data directory")
    parser.add_argument("data_dir", nargs='?', default="../Data",
                       help="Path to Data directory (default: ../Data)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Don't modify files, just show what would be done")

    args = parser.parse_args()

    if not os.path.exists(args.data_dir):
        print(f"Error: Directory not found: {args.data_dir}")
        sys.exit(1)

    fix_all_yaml_files(args.data_dir, dry_run=args.dry_run)
