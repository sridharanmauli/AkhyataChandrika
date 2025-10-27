#!/usr/bin/env python3
"""
Script to remove all entries where 'resolved' is 'true' from YAML files
in the AI_Generated output folders.
"""

import os
import yaml
from pathlib import Path

def process_yaml_file(file_path):
    """
    Process a single YAML file and remove entries where resolved is true.
    Returns True if file was modified, False otherwise.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse YAML
        data = yaml.safe_load(content)

        if not data:
            return False

        # Extract header comments (everything before the first entry)
        header_lines = []
        in_header = True
        for line in content.split('\n'):
            if in_header:
                if line.strip().startswith('#') or line.strip() == '':
                    header_lines.append(line)
                elif line.strip().startswith('"') or (line.strip() and not line.strip().startswith('#')):
                    in_header = False

        # Count entries before removal
        original_count = len(data) if isinstance(data, dict) else 0

        # Remove entries where resolved is true
        if isinstance(data, dict):
            entries_to_remove = []
            for key, value in data.items():
                if isinstance(value, dict) and value.get('resolved') == 'true':
                    entries_to_remove.append(key)

            for key in entries_to_remove:
                del data[key]

        new_count = len(data) if isinstance(data, dict) else 0
        removed_count = original_count - new_count

        if removed_count > 0:
            # Update the count in header if present
            updated_header = []
            for line in header_lines:
                if line.startswith('# ENTRIES TO CORRECT:'):
                    updated_header.append(f'# ENTRIES TO CORRECT: {new_count}')
                else:
                    updated_header.append(line)

            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write header
                if updated_header:
                    f.write('\n'.join(updated_header) + '\n\n')

                # Write YAML data
                if data:
                    yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

            print(f"✓ {file_path.name}: Removed {removed_count} resolved entries ({new_count} remaining)")
            return True
        else:
            print(f"  {file_path.name}: No resolved entries found")
            return False

    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

def process_folder(folder_path):
    """
    Process all YAML files in a folder.
    """
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Folder not found: {folder_path}")
        return 0, 0

    yaml_files = list(folder.glob('*.yaml')) + list(folder.glob('*.yml'))
    modified_count = 0
    total_count = len(yaml_files)

    print(f"\nProcessing folder: {folder.name}")
    print(f"Found {total_count} YAML files")
    print("-" * 60)

    for yaml_file in sorted(yaml_files):
        if process_yaml_file(yaml_file):
            modified_count += 1

    return modified_count, total_count

def main():
    """Main function to process all three folders and consolidated files."""
    base_path = Path(__file__).parent / 'output'

    folders = [
        'multipleDhatuIdsWithGati',
        'multipleDhatuIdsWithoutGati',
        'notFoundDhatuIdsWithoutGati'
    ]

    # Consolidated files in the main output directory
    consolidated_files = [
        'multiple_dhatu_ids_with_gati.yaml',
        'multiple_dhatu_ids_without_gati.yaml',
        'not_found_dhatu_ids_without_gati.yaml'
    ]

    total_modified = 0
    total_files = 0

    print("=" * 60)
    print("Removing entries where resolved='true'")
    print("=" * 60)

    # Process folders
    for folder in folders:
        folder_path = base_path / folder
        modified, total = process_folder(folder_path)
        total_modified += modified
        total_files += total

    # Process consolidated files
    print(f"\nProcessing consolidated files in output directory")
    print("-" * 60)
    for filename in consolidated_files:
        file_path = base_path / filename
        if file_path.exists():
            if process_yaml_file(file_path):
                total_modified += 1
            total_files += 1
        else:
            print(f"File not found: {filename}")

    print("\n" + "=" * 60)
    print(f"Summary: Modified {total_modified} out of {total_files} files")
    print("=" * 60)

if __name__ == '__main__':
    main()
