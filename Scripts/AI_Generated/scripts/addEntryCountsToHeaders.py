#!/usr/bin/env python3
"""
Script to add entry counts to the header of each split file.

This script updates the header comments to include the number of entries
that need to be corrected in each file.
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


def write_yaml_with_header(yaml_file, data, header_lines):
    """Write YAML data to file with custom header"""
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


def update_folder(folder_path, file_type):
    """Update all files in a folder with entry counts"""
    print(f"\n{'='*70}")
    print(f"Processing: {os.path.basename(folder_path)}")
    print(f"{'='*70}\n")

    part_files = sorted([f for f in os.listdir(folder_path)
                         if f.startswith('part_') and f.endswith('.yaml')])

    for part_file in part_files:
        part_path = os.path.join(folder_path, part_file)
        part_num = part_file.replace('part_', '').replace('.yaml', '')

        # Load the file
        data = load_yaml_file(part_path)
        entry_count = len(data)

        # Create updated header
        if file_type == 'multiple_dhatu_ids':
            header = [
                "# Cases where a verb has more than one dhatu_id",
                "# Format: Each entry shows the verb form with its multiple dhatu_ids",
                "# Manually edit this file to select the correct dhatu_id for each case",
                "# After editing, run the backport script to sync changes back to original YAML files",
                "# ",
                f"# ENTRIES TO CORRECT: {entry_count}",
                f"# This is part {int(part_num)} of 10 - Assigned for proofreading"
            ]
        else:  # not_found_dhatu_ids
            header = [
                "# Cases where a verb has 'Not Found' dhatu_id (verbs WITHOUT gati)",
                "# Format: Each entry shows the verb form that needs a dhatu_id assigned",
                "# Manually edit this file to add the correct dhatu_id for each case",
                "# After editing, run the backport script to sync changes back to original YAML files",
                "#",
                "# Instructions:",
                "#   1. Find the correct dhatu_id for each verb",
                "#   2. Change dhatu_id from 'Not Found' to the correct ID (e.g., '01.0594')",
                "#   3. Keep the gati field as is (don't modify it)",
                "#   4. Run backport script to apply changes",
                "#",
                f"# ENTRIES TO CORRECT: {entry_count}",
                f"# This is part {int(part_num)} of 10 - Assigned for proofreading"
            ]

        # Write updated file
        write_yaml_with_header(part_path, data, header)
        print(f"  ✅ Updated {part_file}: {entry_count} entries")

    print(f"\n  Total files updated: {len(part_files)}")


def main():
    """Main function"""
    print("\n" + "="*70)
    print("Adding Entry Counts to File Headers")
    print("="*70)

    folders = [
        {
            'path': 'Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati',
            'type': 'multiple_dhatu_ids'
        },
        {
            'path': 'Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati',
            'type': 'not_found_dhatu_ids'
        }
    ]

    for folder_info in folders:
        folder_path = folder_info['path']
        file_type = folder_info['type']

        if not os.path.exists(folder_path):
            print(f"\n❌ Error: Folder not found: {folder_path}")
            continue

        update_folder(folder_path, file_type)

    print("\n" + "="*70)
    print("✅ All files updated with entry counts!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
