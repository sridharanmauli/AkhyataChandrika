#!/usr/bin/env python3
"""
Script to remove entries marked as resolved=true from split files.

This script:
1. Reads all part_*.yaml files in the folders
2. Removes entries where resolved=true
3. Keeps entries where resolved=false
4. Updates the files and entry counts
5. Reports statistics on removed entries
"""

import yaml
import os
import sys
from collections import OrderedDict

# Custom YAML dumper and loader
class QuotedDumper(yaml.SafeDumper):
    pass

def quoted_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

def ordered_dict_representer(dumper, data):
    return dumper.represent_dict(data.items())

yaml.add_representer(str, quoted_str_representer, Dumper=QuotedDumper)
yaml.add_representer(OrderedDict, ordered_dict_representer, Dumper=QuotedDumper)

class ForceStringLoader(yaml.SafeLoader):
    pass

def str_constructor(loader, node):
    return loader.construct_scalar(node)

def dict_constructor(loader, node):
    return OrderedDict(loader.construct_pairs(node))

ForceStringLoader.add_constructor(u'tag:yaml.org,2002:int', str_constructor)
ForceStringLoader.add_constructor(u'tag:yaml.org,2002:float', str_constructor)
ForceStringLoader.add_constructor(u'tag:yaml.org,2002:map', dict_constructor)


def load_yaml_file(yaml_file):
    """Load a YAML file"""
    with open(yaml_file, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=ForceStringLoader)


def read_header_lines(yaml_file):
    """Read header comment lines from YAML file"""
    header_lines = []
    with open(yaml_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'):
                header_lines.append(line.rstrip())
            elif line.strip():  # Stop at first non-comment, non-empty line
                break
    return header_lines


def update_header_entry_count(header_lines, new_count):
    """Update the ENTRIES TO CORRECT count in header"""
    updated_header = []
    for line in header_lines:
        if 'ENTRIES TO CORRECT:' in line:
            # Replace the number
            updated_header.append(f"# ENTRIES TO CORRECT: {new_count}")
        else:
            updated_header.append(line)
    return updated_header


def write_yaml_with_header(yaml_file, data, header_lines):
    """Write YAML data to file with header"""
    with open(yaml_file, 'w', encoding='utf-8') as f:
        # Write header
        for line in header_lines:
            f.write(f"{line}\n")
        f.write("\n")

        # Write YAML data
        yaml.dump(
            data,
            f,
            allow_unicode=True,
            default_flow_style=False,
            indent=2,
            sort_keys=False,
            width=1000,
            Dumper=QuotedDumper
        )


def remove_resolved_from_folder(folder_path, dry_run=False):
    """Remove resolved entries from all files in a folder"""
    print(f"\n{'='*70}")
    print(f"Processing: {os.path.basename(folder_path)}")
    print(f"{'='*70}\n")

    part_files = sorted([f for f in os.listdir(folder_path)
                         if f.startswith('part_') and f.endswith('.yaml')])

    total_before = 0
    total_after = 0
    total_removed = 0
    files_with_changes = 0

    for part_file in part_files:
        part_path = os.path.join(folder_path, part_file)

        # Read header
        header_lines = read_header_lines(part_path)

        # Load data
        data = load_yaml_file(part_path)
        original_count = len(data)
        total_before += original_count

        # Filter out resolved entries
        unresolved_data = OrderedDict()
        resolved_entries = []

        for key, entry in data.items():
            if isinstance(entry, dict):
                resolved_value = entry.get('resolved', 'false')
                # Check if resolved is true (handle both string and boolean)
                if resolved_value == 'true' or resolved_value == True:
                    resolved_entries.append(key)
                else:
                    unresolved_data[key] = entry

        removed_count = len(resolved_entries)
        new_count = len(unresolved_data)
        total_after += new_count
        total_removed += removed_count

        if removed_count > 0:
            files_with_changes += 1
            print(f"  📝 {part_file}:")
            print(f"     Before: {original_count} entries")
            print(f"     After:  {new_count} entries")
            print(f"     Removed: {removed_count} resolved entries")

            if not dry_run:
                # Update header with new count
                updated_header = update_header_entry_count(header_lines, new_count)

                # Write updated file
                write_yaml_with_header(part_path, unresolved_data, updated_header)
                print(f"     ✅ File updated")
            else:
                print(f"     🔍 [DRY RUN] Would remove:")
                for entry in resolved_entries[:3]:  # Show first 3
                    print(f"        - {entry}")
                if len(resolved_entries) > 3:
                    print(f"        ... and {len(resolved_entries) - 3} more")
        else:
            print(f"  ⏭️  {part_file}: No resolved entries")

    print(f"\n{'='*70}")
    print(f"Summary for {os.path.basename(folder_path)}:")
    print(f"  Total entries before:  {total_before}")
    print(f"  Total entries after:   {total_after}")
    print(f"  Total removed:         {total_removed}")
    print(f"  Files with changes:    {files_with_changes}/{len(part_files)}")
    print(f"{'='*70}")

    return total_before, total_after, total_removed


def main():
    """Main function"""
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv

    print("\n" + "="*70)
    if dry_run:
        print("REMOVE RESOLVED ENTRIES - DRY RUN MODE")
        print("(No files will be modified)")
    else:
        print("REMOVE RESOLVED ENTRIES")
    print("="*70)

    folders = [
        'Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati',
        'Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati'
    ]

    grand_total_before = 0
    grand_total_after = 0
    grand_total_removed = 0

    for folder_path in folders:
        if not os.path.exists(folder_path):
            print(f"\n❌ Error: Folder not found: {folder_path}")
            continue

        before, after, removed = remove_resolved_from_folder(folder_path, dry_run)
        grand_total_before += before
        grand_total_after += after
        grand_total_removed += removed

    print("\n" + "="*70)
    print("GRAND TOTAL:")
    print("="*70)
    print(f"  Entries before:  {grand_total_before}")
    print(f"  Entries after:   {grand_total_after}")
    print(f"  Total removed:   {grand_total_removed}")

    if dry_run:
        print("\n🔍 This was a dry run. No files were modified.")
        print("   Run without --dry-run to actually remove resolved entries.")
    else:
        print("\n✅ Resolved entries have been removed!")
        print("   Entry counts in file headers have been updated.")

    print("="*70 + "\n")

    if dry_run:
        print("Usage:")
        print("  Dry run:  python3 Scripts/AI_Generated/scripts/removeResolvedEntries.py --dry-run")
        print("  Execute:  python3 Scripts/AI_Generated/scripts/removeResolvedEntries.py")
        print()


if __name__ == "__main__":
    main()
