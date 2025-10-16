#!/usr/bin/env python3
"""
Script to backport manually edited dhatu_id changes from the multiple_dhatu_ids YAML files
back to the original YAML files in the Data folder.

Location: Scripts/AI_Generated/scripts/backportMultipleDhatuIds.py

Usage (from project root):
    # Process all files in output directory:
    python3 Scripts/AI_Generated/scripts/backportMultipleDhatuIds.py \\
        Scripts/AI_Generated/output \\
        Data

    # Or process a single file:
    python3 Scripts/AI_Generated/scripts/backportMultipleDhatuIds.py \\
        Scripts/AI_Generated/output/multiple_dhatu_ids_without_gati.yaml \\
        Data

This script:
1. Reads the manually edited YAML file(s)
2. For each entry, finds the corresponding verb in the original YAML files
3. Updates the dhatu_id field in the original YAML files
4. Reports all changes made
"""

import yaml
import sys
import os
from collections import OrderedDict

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


def load_multiple_dhatu_ids(yaml_file):
    """Load the multiple_dhatu_ids.yaml file"""
    with open(yaml_file, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=ForceStringLoader)


def find_yaml_file(data_folder, kanda_name, varga_name, adhikaar=None):
    """
    Find the YAML file path for a given kanda, varga, and optionally adhikaar.

    Returns: Path to the YAML file, or None if not found
    """
    # Map kanda names to IDs
    kanda_map = {
        'प्रथमकाण्डः': '1',
        'द्वितीयकाण्डः': '2',
        'तृतीयकाण्डः': '3'
    }

    kanda_id = kanda_map.get(kanda_name)
    if not kanda_id:
        return None

    kanda_folder = os.path.join(data_folder, f"{kanda_id}_{kanda_name}")

    if not os.path.exists(kanda_folder):
        return None

    # Check if this is नानार्थवर्गः (skip these files)
    if 'नानार्थवर्गः' in varga_name:
        print(f"  ⏭️  Skipping नानार्थवर्गः: {varga_name}")
        return None

    # If adhikaar is specified, this is a sub-varga file
    if adhikaar:
        # Map adhikaar names to file numbers
        adhikaar_to_file = {
            'भ्वादिगणः': '1',
            'अदादिगणः': '2',
            'जुहोत्यादिगणः': '3',
            'दिवादिगणः': '4',
            'स्वादिगणः': '5',
            'तुदादिगणः': '6',
            'रुधादिगणः': '7',
            'तनादिगणः': '8',
            'क्रयादिगणः': '9',
            'चुरादिगणः': '10',
            'नामधातवः': '11',
            'कण्ड्वादयः': '12'
        }

        file_num = adhikaar_to_file.get(adhikaar)
        if not file_num:
            return None

        # Try to find the varga folder
        for item in os.listdir(kanda_folder):
            if varga_name in item and os.path.isdir(os.path.join(kanda_folder, item)):
                varga_folder = os.path.join(kanda_folder, item)
                yaml_file = os.path.join(varga_folder, f"{file_num}_{adhikaar}.yaml")
                if os.path.exists(yaml_file):
                    return yaml_file
                break
    else:
        # Regular varga (single YAML file)
        for item in os.listdir(kanda_folder):
            if varga_name in item and item.endswith('.yaml'):
                yaml_file = os.path.join(kanda_folder, item)
                if os.path.exists(yaml_file):
                    return yaml_file

    return None


def update_verb_in_yaml(yaml_data, shloka_text, artha, form, new_dhatu_ids, gati):
    """
    Update a specific verb's dhatu_id in the YAML data structure.

    Returns: True if updated, False if not found
    """
    # Find the shloka
    for shloka_key in yaml_data.keys():
        if shloka_text.strip() in shloka_key or shloka_key.strip() in shloka_text:
            shloka_data = yaml_data[shloka_key]

            if not shloka_data or not isinstance(shloka_data, dict):
                continue

            # Find the artha
            if artha in shloka_data:
                artha_data = shloka_data[artha]

                if not isinstance(artha_data, dict):
                    continue

                # Find the verb form
                if form in artha_data:
                    # Update the dhatu_id
                    if gati and gati.strip():
                        # Has gati: format is [gati, dhatu_id]
                        yaml_data[shloka_key][artha][form] = [gati, new_dhatu_ids]
                    else:
                        # No gati: format is [dhatu_id]
                        yaml_data[shloka_key][artha][form] = [new_dhatu_ids]

                    return True

    return False


def write_yaml_file(yaml_file, data):
    """Write YAML data to file with proper formatting"""
    with open(yaml_file, 'w', encoding='utf-8') as f:
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


def backport_changes(multiple_dhatu_ids_yaml, data_folder):
    """
    Backport changes from multiple_dhatu_ids.yaml to original YAML files.
    """
    print(f"📚 Loading multiple dhatu_ids from {multiple_dhatu_ids_yaml}...")
    changes_data = load_multiple_dhatu_ids(multiple_dhatu_ids_yaml)

    if not changes_data:
        print("❌ No data found in multiple_dhatu_ids.yaml")
        return

    total_entries = len(changes_data)
    updated_files = set()
    updated_count = 0
    not_found_count = 0

    print(f"\n{'='*60}")
    print(f"Processing {total_entries} entries...")
    print(f"{'='*60}\n")

    for key, entry_data in changes_data.items():
        # Extract only the fields needed for backporting
        # Note: 'resolved' and 'comment' fields are ignored (used only for proofreading workflow)
        form = entry_data.get('form')
        dhatu_ids = entry_data.get('dhatu_ids')
        gati = entry_data.get('gati', '')
        kanda = entry_data.get('kanda')
        varga = entry_data.get('varga')
        adhikaar = entry_data.get('adhikaar', '')
        artha = entry_data.get('artha')
        shloka_text = entry_data.get('shloka_text')

        print(f"Processing: {key}")
        print(f"  Form: {form}, Dhatu IDs: {dhatu_ids}, Gati: {gati}")

        # Find the YAML file
        yaml_file = find_yaml_file(data_folder, kanda, varga, adhikaar if adhikaar else None)

        if not yaml_file:
            print(f"  ❌ YAML file not found for: {kanda} / {varga} / {adhikaar}")
            not_found_count += 1
            continue

        print(f"  📁 Found: {yaml_file}")

        # Load the YAML file
        with open(yaml_file, 'r', encoding='utf-8') as f:
            yaml_data = yaml.load(f, Loader=ForceStringLoader)

        # Update the verb in the YAML data
        if update_verb_in_yaml(yaml_data, shloka_text, artha, form, dhatu_ids, gati):
            # Write the updated YAML back to file
            write_yaml_file(yaml_file, yaml_data)
            updated_files.add(yaml_file)
            updated_count += 1
            print(f"  ✅ Updated: {form} → {dhatu_ids}")
        else:
            print(f"  ⚠️  Verb not found in YAML: {form} in artha '{artha}'")
            not_found_count += 1

        print()

    print(f"\n{'='*60}")
    print(f"✅ Backport complete!")
    print(f"  Total entries processed: {total_entries}")
    print(f"  Successfully updated: {updated_count}")
    print(f"  Not found or skipped: {not_found_count}")
    print(f"  Files modified: {len(updated_files)}")
    print(f"{'='*60}\n")

    if updated_files:
        print("📝 Modified files:")
        for file_path in sorted(updated_files):
            print(f"  - {file_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 Scripts/AI_Generated/scripts/backportMultipleDhatuIds.py <yaml_file_or_dir> <data_folder>")
        print("\nOptions:")
        print("  1. Process all YAML files in output directory (recommended):")
        print("     python3 Scripts/AI_Generated/scripts/backportMultipleDhatuIds.py \\")
        print("         Scripts/AI_Generated/output \\")
        print("         Data")
        print("\n  2. Process a single YAML file:")
        print("     python3 Scripts/AI_Generated/scripts/backportMultipleDhatuIds.py \\")
        print("         Scripts/AI_Generated/output/multiple_dhatu_ids_without_gati.yaml \\")
        print("         Data")
        print("\nNote: This will process both *_without_gati.yaml and *_with_gati.yaml files when given a directory")
        sys.exit(1)

    yaml_input = sys.argv[1]
    data_folder = sys.argv[2]

    if not os.path.exists(data_folder):
        print(f"❌ Error: Data folder not found: {data_folder}")
        sys.exit(1)

    # Check if input is a directory or a file
    yaml_files = []

    if os.path.isdir(yaml_input):
        # Process all relevant YAML files in the directory
        print(f"📂 Processing directory: {yaml_input}")
        for filename in os.listdir(yaml_input):
            # Support both old naming (multiple_dhatu_ids_*.yaml) and new split naming (part_*.yaml)
            if (filename.startswith("multiple_dhatu_ids_") or filename.startswith("part_")) and filename.endswith(".yaml"):
                yaml_files.append(os.path.join(yaml_input, filename))

        if not yaml_files:
            print(f"❌ Error: No multiple_dhatu_ids_*.yaml or part_*.yaml files found in {yaml_input}")
            sys.exit(1)

        print(f"Found {len(yaml_files)} file(s) to process:")
        for f in yaml_files:
            print(f"  - {os.path.basename(f)}")
        print()

    elif os.path.isfile(yaml_input):
        # Process single file
        yaml_files.append(yaml_input)
    else:
        print(f"❌ Error: File or directory not found: {yaml_input}")
        sys.exit(1)

    # Process each YAML file
    for i, yaml_file in enumerate(yaml_files, 1):
        print(f"\n{'='*70}")
        print(f"Processing file {i}/{len(yaml_files)}: {os.path.basename(yaml_file)}")
        print(f"{'='*70}")
        backport_changes(yaml_file, data_folder)

    if len(yaml_files) > 1:
        print(f"\n{'='*70}")
        print(f"✅ All {len(yaml_files)} files processed successfully!")
        print(f"{'='*70}")
