#!/usr/bin/env python3
"""
Script to add 'resolved' and 'comment' fields to all entries in split files.

This script:
1. Adds 'resolved: false' to each entry
2. Adds 'comment: ""' to each entry
3. These fields are for proofreading workflow only (not backported)
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


def add_review_fields_to_folder(folder_path):
    """Add resolved and comment fields to all entries in a folder"""
    print(f"\n{'='*70}")
    print(f"Processing: {os.path.basename(folder_path)}")
    print(f"{'='*70}\n")

    part_files = sorted([f for f in os.listdir(folder_path)
                         if f.startswith('part_') and f.endswith('.yaml')])

    total_entries = 0

    for part_file in part_files:
        part_path = os.path.join(folder_path, part_file)

        # Read header
        header_lines = read_header_lines(part_path)

        # Load data
        data = load_yaml_file(part_path)

        # Add resolved and comment fields to each entry
        for key, entry in data.items():
            if isinstance(entry, dict):
                # Add resolved field if not present
                if 'resolved' not in entry:
                    entry['resolved'] = 'false'

                # Add comment field if not present
                if 'comment' not in entry:
                    entry['comment'] = ''

        # Write updated file
        write_yaml_with_header(part_path, data, header_lines)

        total_entries += len(data)
        print(f"  ✅ Updated {part_file}: {len(data)} entries")

    print(f"\n  Total entries updated: {total_entries}")
    print(f"  Total files: {len(part_files)}")


def main():
    """Main function"""
    print("\n" + "="*70)
    print("Adding Review Fields (resolved, comment) to All Entries")
    print("="*70)

    folders = [
        'Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati',
        'Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati'
    ]

    for folder_path in folders:
        if not os.path.exists(folder_path):
            print(f"\n❌ Error: Folder not found: {folder_path}")
            continue

        add_review_fields_to_folder(folder_path)

    print("\n" + "="*70)
    print("✅ All files updated with review fields!")
    print("="*70)
    print("\nAdded fields to each entry:")
    print("  - resolved: false (default)")
    print("  - comment: '' (empty by default)")
    print("\nProofreaders can now:")
    print("  1. Set resolved=true when done reviewing an entry")
    print("  2. Add comments for any notes or issues")
    print("  3. Run cleanup script to remove resolved entries")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
