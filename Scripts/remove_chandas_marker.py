#!/usr/bin/env python3
"""
Script to remove (छ) marker from verb forms in JSON and YAML files.
The marker indicates Chandasa Prayoga, but should be removed from the form field
since we now have a dedicated 'type: chandas' field in JSON.
"""

import json
import yaml
import re
from pathlib import Path

def process_json_file(file_path):
    """
    Process the JSON file and remove (छ) marker from form fields.
    Also removes extra trailing spaces.
    Returns count of modified entries.
    """
    print(f"Processing JSON file: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    modified_count = 0

    # Navigate through the nested structure
    for kanda in data.get('data', []):
        for varga in kanda.get('vargas', []):
            for shloka in varga.get('shlokas', []):
                for verb_group in shloka.get('verbs', []):
                    for entry in verb_group.get('entries', []):
                        form = entry.get('form', '')

                        # Check if form contains (छ)
                        if '(छ)' in form or '(छ)' in form:
                            # Remove (छ) marker and trim spaces
                            old_form = form
                            new_form = form.replace('(छ)', '').replace('(छ)', '').strip()

                            if old_form != new_form:
                                entry['form'] = new_form
                                modified_count += 1
                                print(f"  ✓ '{old_form}' → '{new_form}'")

    if modified_count > 0:
        print(f"\nWriting changes back to JSON file...")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✓ Successfully modified {modified_count} entries in JSON")
    else:
        print("No (छ) markers found in JSON")

    return modified_count

def process_yaml_file(file_path):
    """
    Process a single YAML file and remove (छ) marker from form fields and keys.
    Returns count of modified entries.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse YAML
        data = yaml.safe_load(content)

        if not data:
            return 0

        modified_count = 0
        modified = False

        # Process each entry - need to handle key renaming
        if isinstance(data, dict):
            new_data = {}
            for key, value in data.items():
                # Check if key needs to be modified
                new_key = key
                if '(छ)' in key or '(छ)' in key:
                    new_key = key.replace('(छ)', '').replace('(छ)', '').strip()
                    modified = True
                    modified_count += 1

                # Check if form field needs to be modified
                if isinstance(value, dict):
                    form = value.get('form', '')
                    if '(छ)' in form or '(छ)' in form:
                        old_form = form
                        new_form = form.replace('(छ)', '').replace('(छ)', '').strip()
                        if old_form != new_form:
                            value['form'] = new_form
                            if new_key == key:  # Only count if we didn't already count the key change
                                modified_count += 1
                            modified = True

                new_data[new_key] = value

            data = new_data

        if modified:
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            return modified_count

        return 0

    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return 0

def process_yaml_files(base_path):
    """
    Process all YAML files in the output directory.
    """
    total_modified = 0
    files_modified = 0

    # Process consolidated files
    yaml_files = list(base_path.glob('*.yaml'))
    yaml_files.extend(base_path.glob('*.yml'))

    # Process files in subdirectories
    for subdir in ['multipleDhatuIdsWithGati', 'multipleDhatuIdsWithoutGati', 'notFoundDhatuIdsWithoutGati']:
        subdir_path = base_path / subdir
        if subdir_path.exists():
            yaml_files.extend(subdir_path.glob('*.yaml'))
            yaml_files.extend(subdir_path.glob('*.yml'))

    print(f"\nProcessing {len(yaml_files)} YAML files...")
    print("-" * 70)

    for yaml_file in sorted(yaml_files):
        modified = process_yaml_file(yaml_file)
        if modified > 0:
            total_modified += modified
            files_modified += 1
            print(f"  ✓ {yaml_file.name}: Removed (छ) from {modified} entries")

    return total_modified, files_modified

def main():
    """Main function."""
    script_dir = Path(__file__).parent
    json_file = script_dir / 'output' / 'AkhyataChandrika_Autogenerated.json'
    yaml_base_path = script_dir / 'AI_Generated' / 'output'

    print("=" * 70)
    print("Removing (छ) marker from verb forms")
    print("=" * 70)
    print()

    # Process JSON file
    if json_file.exists():
        json_modified = process_json_file(json_file)
    else:
        print(f"Warning: JSON file not found at {json_file}")
        json_modified = 0

    # Process YAML files
    if yaml_base_path.exists():
        yaml_modified, yaml_files = process_yaml_files(yaml_base_path)
    else:
        print(f"Warning: YAML directory not found at {yaml_base_path}")
        yaml_modified = 0
        yaml_files = 0

    print("\n" + "=" * 70)
    print(f"Summary:")
    print(f"  JSON: Modified {json_modified} entries")
    print(f"  YAML: Modified {yaml_modified} entries across {yaml_files} files")
    print(f"  Total: {json_modified + yaml_modified} modifications")
    print("=" * 70)

if __name__ == '__main__':
    main()
