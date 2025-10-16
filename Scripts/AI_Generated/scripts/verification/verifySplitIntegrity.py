#!/usr/bin/env python3
"""
Script to verify that splitting did not lose any data.

This script:
1. Loads the original YAML files
2. Loads all split part files
3. Compares entries to ensure no data loss
4. Reports any discrepancies
"""

import yaml
import os
import sys
from collections import OrderedDict

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


def verify_split(original_file, split_folder, file_type):
    """
    Verify that split files contain all data from original file.

    Returns: (is_valid, original_count, split_count, missing_keys, extra_keys)
    """
    print(f"\n{'='*70}")
    print(f"Verifying: {os.path.basename(original_file)}")
    print(f"{'='*70}\n")

    # Load original file
    print(f"📚 Loading original file...")
    original_data = load_yaml_file(original_file)
    original_keys = set(original_data.keys())
    original_count = len(original_data)
    print(f"   Original entries: {original_count}")

    # Load all split files
    print(f"📁 Loading split files from {os.path.basename(split_folder)}...")
    combined_data = OrderedDict()
    part_files = sorted([f for f in os.listdir(split_folder) if f.startswith('part_') and f.endswith('.yaml')])

    for part_file in part_files:
        part_path = os.path.join(split_folder, part_file)
        part_data = load_yaml_file(part_path)
        print(f"   {part_file}: {len(part_data)} entries")
        combined_data.update(part_data)

    split_keys = set(combined_data.keys())
    split_count = len(combined_data)

    print(f"\n📊 Summary:")
    print(f"   Total split entries: {split_count}")
    print(f"   Original entries:    {original_count}")

    # Check for missing or extra keys
    missing_keys = original_keys - split_keys
    extra_keys = split_keys - original_keys

    is_valid = (original_count == split_count and
                len(missing_keys) == 0 and
                len(extra_keys) == 0)

    if is_valid:
        print(f"   ✅ Status: VALID - All entries match!")

        # Deep comparison of data
        print(f"\n🔍 Deep comparison of data...")
        all_match = True
        for key in original_keys:
            if original_data[key] != combined_data[key]:
                print(f"   ⚠️  Data mismatch for key: {key}")
                all_match = False

        if all_match:
            print(f"   ✅ All data matches perfectly!")
        else:
            is_valid = False
    else:
        print(f"   ❌ Status: INVALID - Discrepancies found!")

        if missing_keys:
            print(f"\n   ❌ Missing {len(missing_keys)} entries in split files:")
            for key in list(missing_keys)[:5]:
                print(f"      - {key}")
            if len(missing_keys) > 5:
                print(f"      ... and {len(missing_keys) - 5} more")

        if extra_keys:
            print(f"\n   ⚠️  Found {len(extra_keys)} extra entries in split files:")
            for key in list(extra_keys)[:5]:
                print(f"      - {key}")
            if len(extra_keys) > 5:
                print(f"      ... and {len(extra_keys) - 5} more")

    return is_valid, original_count, split_count, missing_keys, extra_keys


def main():
    """Main verification function"""
    print("\n" + "="*70)
    print("YAML Split Integrity Verification")
    print("="*70)

    # Define file paths
    files_to_verify = [
        {
            'original': 'Scripts/AI_Generated/output/multiple_dhatu_ids_without_gati.yaml',
            'split': 'Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati',
            'type': 'multiple_dhatu_ids'
        },
        {
            'original': 'Scripts/AI_Generated/output/not_found_dhatu_ids_without_gati.yaml',
            'split': 'Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati',
            'type': 'not_found_dhatu_ids'
        }
    ]

    all_valid = True
    results = []

    for file_info in files_to_verify:
        original_file = file_info['original']
        split_folder = file_info['split']
        file_type = file_info['type']

        if not os.path.exists(original_file):
            print(f"\n❌ Error: Original file not found: {original_file}")
            all_valid = False
            continue

        if not os.path.exists(split_folder):
            print(f"\n❌ Error: Split folder not found: {split_folder}")
            all_valid = False
            continue

        is_valid, orig_count, split_count, missing, extra = verify_split(
            original_file, split_folder, file_type
        )

        results.append({
            'file': os.path.basename(original_file),
            'valid': is_valid,
            'original_count': orig_count,
            'split_count': split_count
        })

        if not is_valid:
            all_valid = False

    # Final summary
    print("\n" + "="*70)
    print("FINAL VERIFICATION SUMMARY")
    print("="*70)

    for result in results:
        status = "✅ PASS" if result['valid'] else "❌ FAIL"
        print(f"{status}: {result['file']}")
        print(f"         Original: {result['original_count']} entries")
        print(f"         Split:    {result['split_count']} entries")
        print()

    if all_valid:
        print("🎉 ALL VERIFICATIONS PASSED!")
        print("✅ It is safe to remove the original files.")
        print("\n" + "="*70 + "\n")
        return 0
    else:
        print("❌ VERIFICATION FAILED!")
        print("⚠️  DO NOT remove original files - data discrepancies found!")
        print("\n" + "="*70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
