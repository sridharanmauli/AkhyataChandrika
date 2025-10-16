#!/usr/bin/env python3
"""
Script to completely rebuild YAML files from the generated JSON.
This ensures YAML files contain all the extra information (dhatu_id, gati)
that was generated during JSON creation.

Use case: People work on YAML -> JSON is generated with extra info ->
This script updates YAML with that extra info so YAML remains the source of truth.
"""

import yaml
import json
import os
import sys
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


def load_json_data(json_file):
    """Load the full JSON file"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def rebuild_yaml_from_json(json_data, kanda_name, varga_name, varga_id, adhikaar=None):
    """
    Rebuild YAML structure from JSON data for a specific varga.

    Returns: OrderedDict with structure:
    {
        "shloka text": {
            "artha": {
                "verb": [gati, dhatu_id] or [dhatu_id] or null
            }
        }
    }
    """
    yaml_data = OrderedDict()

    # Find the kanda and varga in JSON
    for kanda in json_data.get('data', []):
        if kanda.get('kanda_name') != kanda_name:
            continue

        for varga in kanda.get('vargas', []):
            if varga.get('varga_name') != varga_name or varga.get('varga_id') != varga_id:
                continue

            # Process each shloka
            for shloka in varga.get('shlokas', []):
                # Check if we should filter by adhikaar
                shloka_adhikaar = shloka.get('adhikaar')
                if adhikaar is not None and shloka_adhikaar != adhikaar:
                    continue

                shloka_text = shloka.get('text', '').strip()
                # The shloka text already ends with ॥, so just add it as is
                # Check if it already ends with ॥
                if shloka_text.endswith('॥'):
                    shloka_key = f"{shloka_text}"
                else:
                    shloka_key = f"{shloka_text} ॥"

                # Build artha structure
                artha_dict = OrderedDict()

                for verb_block in shloka.get('verbs', []):
                    artha = verb_block.get('artha', '')

                    # Build verb entries for this artha
                    verb_entries = OrderedDict()

                    for entry in verb_block.get('entries', []):
                        form = entry.get('form', '')
                        dhatu_id = entry.get('dhatu_id', '')
                        gati = entry.get('gati', '')

                        # Create the value based on what we have
                        if dhatu_id == "Not Found":
                            # Keep as null
                            verb_entries[form] = None
                        elif gati and gati.strip():
                            # Remove " (More than one)" suffix if present
                            dhatu_clean = dhatu_id.replace(" (More than one)", "")
                            verb_entries[form] = [gati, dhatu_clean]
                        elif dhatu_id:
                            # Remove " (More than one)" suffix if present
                            dhatu_clean = dhatu_id.replace(" (More than one)", "")
                            verb_entries[form] = [dhatu_clean]
                        else:
                            verb_entries[form] = None

                    artha_dict[artha] = verb_entries

                yaml_data[shloka_key] = artha_dict

            break
        break

    return yaml_data


def rebuild_yaml_from_json_nanartha(json_data, kanda_name, varga_name, adhikaar):
    """
    Rebuild YAML structure from JSON data for Nanartha Varga.

    In Nanartha Varga, the YAML structure is special:
    - Shloka line has ": null"
    - Then verb forms are at root level
    - Each verb has a list of artha dicts

    Example:
    "shloka ॥": null
    भवति:
      - सत्तायाम्:
        - "01.0001"
    प्रभवति:
      - प्राप्तौ:
        - "प्र"
        - "01.0001"
    """
    yaml_data = OrderedDict()

    # Find the kanda and varga in JSON
    for kanda in json_data.get('data', []):
        if kanda.get('kanda_name') != kanda_name:
            continue

        for varga in kanda.get('vargas', []):
            if varga.get('varga_name') != varga_name:
                continue

            # Group shlokas by shloka text
            shloka_groups = OrderedDict()

            for shloka in varga.get('shlokas', []):
                # Check if this shloka belongs to the specific adhikaar
                shloka_adhikaar = shloka.get('adhikaar')
                if shloka_adhikaar != adhikaar:
                    continue

                shloka_text = shloka.get('text', '').strip()

                if shloka_text not in shloka_groups:
                    shloka_groups[shloka_text] = []

                shloka_groups[shloka_text].append(shloka)

            # Process each shloka group
            for shloka_text, shlokas in shloka_groups.items():
                # Add shloka line with null value
                # The shloka text already ends with ॥
                if shloka_text.endswith('॥'):
                    shloka_key = f"{shloka_text}"
                else:
                    shloka_key = f"{shloka_text} ॥"
                yaml_data[shloka_key] = None

                # Collect all verbs for this shloka
                form_dict = OrderedDict()

                for shloka in shlokas:
                    for verb_block in shloka.get('verbs', []):
                        artha = verb_block.get('artha', '')

                        for entry in verb_block.get('entries', []):
                            form = entry.get('form', '')
                            dhatu_id = entry.get('dhatu_id', '')
                            gati = entry.get('gati', '')

                            # Initialize form entry if not exists
                            if form not in form_dict:
                                form_dict[form] = []

                            # Create artha entry as a dict
                            if dhatu_id == "Not Found":
                                form_dict[form].append({artha: None})
                            elif gati and gati.strip():
                                dhatu_clean = dhatu_id.replace(" (More than one)", "")
                                form_dict[form].append({artha: [gati, dhatu_clean]})
                            elif dhatu_id:
                                dhatu_clean = dhatu_id.replace(" (More than one)", "")
                                form_dict[form].append({artha: [dhatu_clean]})
                            else:
                                form_dict[form].append({artha: None})

                # Add all verb forms at root level
                for form, artha_list in form_dict.items():
                    yaml_data[form] = artha_list

            break
        break

    return yaml_data


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


def process_all_yaml_files(data_folder, json_file):
    """
    Rebuild all YAML files from JSON data.
    """
    print(f"📚 Loading JSON from {json_file}...")
    json_data = load_json_data(json_file)

    total_files = 0

    # Process each Kanda
    for kanda in json_data.get('data', []):
        kanda_name = kanda.get('kanda_name')
        kanda_id = kanda.get('kanda_id')
        kanda_folder = os.path.join(data_folder, f"{kanda_id}_{kanda_name}")

        if not os.path.exists(kanda_folder):
            print(f"⚠️  Kanda folder not found: {kanda_folder}")
            continue

        print(f"\n{'='*60}")
        print(f"Processing Kanda: {kanda_name}")
        print(f"{'='*60}")

        # Process each Varga
        for varga in kanda.get('vargas', []):
            varga_name = varga.get('varga_name')
            varga_id = varga.get('varga_id')

            # Check if this is Nanartha Varga
            is_nanartha = 'नानार्थवर्गः' in varga_name

            # Check if this varga has sub-vargas (mangalam field indicates sub-vargas)
            if 'mangalam' in varga and varga.get('mangalam'):
                # Skip Nanartha Varga - don't touch these files
                if is_nanartha:
                    print(f"\n📂 Skipping Nanartha Varga: {varga_name} (won't be modified)")
                    continue

                # This is a varga with sub-vargas (not Nanartha)
                varga_folder = os.path.join(kanda_folder, f"{varga_id}_{varga_name}")

                if not os.path.exists(varga_folder):
                    print(f"⚠️  Varga folder not found: {varga_folder}")
                    continue

                print(f"\n📂 Processing Varga with sub-sections: {varga_name}")

                # Get all unique adhikaars from shlokas
                adhikaars = set()
                for shloka in varga.get('shlokas', []):
                    adhikaar = shloka.get('adhikaar')
                    if adhikaar:
                        adhikaars.add(adhikaar)

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

                # Process each adhikaar
                for adhikaar in sorted(adhikaars):
                    if adhikaar not in adhikaar_to_file:
                        print(f"  ⚠️  Unknown adhikaar: {adhikaar}")
                        continue

                    file_num = adhikaar_to_file[adhikaar]
                    yaml_file = os.path.join(varga_folder, f"{file_num}_{adhikaar}.yaml")

                    if not os.path.exists(yaml_file):
                        print(f"  ⚠️  YAML file not found: {yaml_file}")
                        continue

                    print(f"\n  📝 Rebuilding: {yaml_file}")

                    yaml_data = rebuild_yaml_from_json(
                        json_data, kanda_name, varga_name, varga_id, adhikaar
                    )

                    if yaml_data:
                        write_yaml_file(yaml_file, yaml_data)
                        print(f"  ✅ Rebuilt {yaml_file} with {len(yaml_data)} shlokas")
                        total_files += 1
                    else:
                        print(f"  ℹ️  No data found for {adhikaar}")

            else:
                # Regular varga (single YAML file)
                yaml_file = os.path.join(kanda_folder, f"{varga_id}_{varga_name}.yaml")

                if not os.path.exists(yaml_file):
                    print(f"⚠️  YAML file not found: {yaml_file}")
                    continue

                print(f"\n📂 Processing Varga: {varga_name}")
                print(f"📝 Rebuilding: {yaml_file}")

                yaml_data = rebuild_yaml_from_json(
                    json_data, kanda_name, varga_name, varga_id, adhikaar=None
                )

                if yaml_data:
                    write_yaml_file(yaml_file, yaml_data)
                    print(f"✅ Rebuilt {yaml_file} with {len(yaml_data)} shlokas")
                    total_files += 1
                else:
                    print(f"ℹ️  No data found for {varga_name}")

    print(f"\n{'='*60}")
    print(f"✅ Complete! Rebuilt {total_files} YAML files")
    print(f"{'='*60}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 populateYamlFromJson.py <data_folder> <json_file>")
        print("Example: python3 populateYamlFromJson.py Data Scripts/output/AkhyataChandrika_Autogenerated.json")
        sys.exit(1)

    data_folder = sys.argv[1]
    json_file = sys.argv[2]

    if not os.path.exists(data_folder):
        print(f"❌ Error: Data folder not found: {data_folder}")
        sys.exit(1)

    if not os.path.exists(json_file):
        print(f"❌ Error: JSON file not found: {json_file}")
        sys.exit(1)

    process_all_yaml_files(data_folder, json_file)
