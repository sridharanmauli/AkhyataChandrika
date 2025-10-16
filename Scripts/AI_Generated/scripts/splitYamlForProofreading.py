#!/usr/bin/env python3
"""
Script to split large YAML files into multiple smaller files for distributed proofreading.

Location: Scripts/AI_Generated/scripts/splitYamlForProofreading.py

Usage (from project root):
    python3 Scripts/AI_Generated/scripts/splitYamlForProofreading.py

This script:
1. Reads multiple_dhatu_ids.yaml (285 entries) and splits into 10 files (~28-29 entries each)
2. Reads not_found_dhatu_ids_without_gati.yaml (595 entries) and splits into 10 files (~59-60 entries each)
3. Creates folders:
   - Scripts/output/multiple_dhatu_ids/
   - Scripts/AI_Generated/output/not_found_dhatu_ids_without_gati/
4. Creates files named: part_01.yaml, part_02.yaml, ..., part_10.yaml in each folder
"""

import yaml
import os
import sys
from collections import OrderedDict
import math

# Custom YAML dumper to preserve strings and formatting
class QuotedDumper(yaml.SafeDumper):
    pass

def quoted_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

def ordered_dict_representer(dumper, data):
    return dumper.represent_dict(data.items())

yaml.add_representer(str, quoted_str_representer, Dumper=QuotedDumper)
yaml.add_representer(OrderedDict, ordered_dict_representer, Dumper=QuotedDumper)


# Custom loader to force all scalars to strings and preserve order
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


def write_yaml_file(yaml_file, data, header_comments=None):
    """Write YAML data to file with proper formatting"""
    with open(yaml_file, 'w', encoding='utf-8') as f:
        # Write header comments if provided
        if header_comments:
            for comment in header_comments:
                f.write(f"# {comment}\n")
            f.write("\n")

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


def split_dict_into_chunks(data_dict, num_chunks):
    """Split a dictionary into N roughly equal chunks"""
    items = list(data_dict.items())
    total_items = len(items)
    chunk_size = math.ceil(total_items / num_chunks)

    chunks = []
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min(start_idx + chunk_size, total_items)
        chunk_items = items[start_idx:end_idx]

        if chunk_items:  # Only add non-empty chunks
            # Add review fields to each entry
            chunk_with_review_fields = OrderedDict()
            for key, value in chunk_items:
                if isinstance(value, dict):
                    # Add resolved and comment fields for proofreading
                    value['resolved'] = 'false'
                    value['comment'] = ''
                chunk_with_review_fields[key] = value

            chunks.append(chunk_with_review_fields)

    return chunks


def split_yaml_file(input_file, output_folder, num_parts, file_type):
    """
    Split a YAML file into multiple parts

    Args:
        input_file: Path to input YAML file
        output_folder: Folder to write split files
        num_parts: Number of parts to split into
        file_type: Type of file ('multiple_dhatu_ids' or 'not_found_dhatu_ids')
    """
    print(f"\n{'='*70}")
    print(f"Processing: {input_file}")
    print(f"{'='*70}\n")

    # Load the YAML file
    print(f"📚 Loading YAML file...")
    data = load_yaml_file(input_file)

    if not data:
        print(f"❌ No data found in {input_file}")
        return

    total_entries = len(data)
    print(f"✅ Loaded {total_entries} entries")

    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    print(f"📁 Created output folder: {output_folder}")

    # Split into chunks
    print(f"✂️  Splitting into {num_parts} parts...")
    chunks = split_dict_into_chunks(data, num_parts)

    # Prepare header comments based on file type
    if file_type == 'multiple_dhatu_ids':
        header_comments = [
            "Cases where a verb has more than one dhatu_id",
            "Format: Each entry shows the verb form with its multiple dhatu_ids",
            "Manually edit this file to select the correct dhatu_id for each case",
            "After editing, run the backport script to sync changes back to original YAML files",
            "",
            "ENTRIES TO CORRECT: {{entry_count}}",
            f"This is part {{part_num}} of {num_parts} - Assigned for proofreading"
        ]
    else:  # not_found_dhatu_ids
        header_comments = [
            "Cases where a verb has 'Not Found' dhatu_id (verbs WITHOUT gati)",
            "Format: Each entry shows the verb form that needs a dhatu_id assigned",
            "Manually edit this file to add the correct dhatu_id for each case",
            "After editing, run the backport script to sync changes back to original YAML files",
            "",
            "Instructions:",
            "  1. Find the correct dhatu_id for each verb",
            "  2. Change dhatu_id from 'Not Found' to the correct ID (e.g., '01.0594')",
            "  3. Keep the gati field as is (don't modify it)",
            "  4. Run backport script to apply changes",
            "",
            "ENTRIES TO CORRECT: {{entry_count}}",
            f"This is part {{part_num}} of {num_parts} - Assigned for proofreading"
        ]

    # Write each chunk to a separate file
    for i, chunk in enumerate(chunks, 1):
        part_num = f"{i:02d}"
        output_file = os.path.join(output_folder, f"part_{part_num}.yaml")

        # Update header comments with actual part number and entry count
        part_header = [comment.format(part_num=i, entry_count=len(chunk)) for comment in header_comments]

        write_yaml_file(output_file, chunk, part_header)
        print(f"  ✅ Created part_{part_num}.yaml ({len(chunk)} entries)")

    print(f"\n{'='*70}")
    print(f"✅ Split complete!")
    print(f"  Total entries: {total_entries}")
    print(f"  Number of parts: {len(chunks)}")
    print(f"  Output folder: {output_folder}")
    print(f"{'='*70}\n")


def main():
    """Main function to split both YAML files"""
    print("\n" + "="*70)
    print("YAML File Splitter for Distributed Proofreading")
    print("="*70)

    # Define file paths - using the without_gati variants
    multiple_dhatu_ids_file = "Scripts/AI_Generated/output/multiple_dhatu_ids_without_gati.yaml"
    not_found_dhatu_ids_file = "Scripts/AI_Generated/output/not_found_dhatu_ids_without_gati.yaml"

    multiple_dhatu_ids_folder = "Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati"
    not_found_dhatu_ids_folder = "Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati"

    num_parts = 10

    # Check if files exist
    if not os.path.exists(multiple_dhatu_ids_file):
        print(f"❌ Error: File not found: {multiple_dhatu_ids_file}")
        sys.exit(1)

    if not os.path.exists(not_found_dhatu_ids_file):
        print(f"❌ Error: File not found: {not_found_dhatu_ids_file}")
        sys.exit(1)

    # Split multiple_dhatu_ids_without_gati.yaml
    split_yaml_file(
        multiple_dhatu_ids_file,
        multiple_dhatu_ids_folder,
        num_parts,
        'multiple_dhatu_ids'
    )

    # Split not_found_dhatu_ids_without_gati.yaml
    split_yaml_file(
        not_found_dhatu_ids_file,
        not_found_dhatu_ids_folder,
        num_parts,
        'not_found_dhatu_ids'
    )

    print("\n" + "="*70)
    print("🎉 All files split successfully!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Distribute the part_*.yaml files to 10 proofreaders")
    print("  2. Each proofreader edits their assigned part")
    print("  3. After proofreading, run the backport script to apply changes")
    print("\nBackport commands:")
    print("  python3 Scripts/AI_Generated/scripts/backportMultipleDhatuIds.py \\")
    print("      Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati \\")
    print("      Data")
    print()
    print("  python3 Scripts/AI_Generated/scripts/backportNotFoundDhatuIds.py \\")
    print("      Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati \\")
    print("      Data")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
