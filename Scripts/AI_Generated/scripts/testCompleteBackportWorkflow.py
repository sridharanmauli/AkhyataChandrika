#!/usr/bin/env python3
"""
End-to-end test of the complete backport workflow.

This script:
1. Makes a temporary edit to a split file
2. Runs the backport script
3. Verifies the change appears in the Data folder
4. Restores everything to original state
"""

import yaml
import os
import sys
import shutil
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


def write_yaml_file(yaml_file, data):
    """Write YAML data to file"""
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


def find_data_yaml_file(kanda, varga, adhikaar=''):
    """Find the corresponding YAML file in Data folder"""
    kanda_map = {
        'प्रथमकाण्डः': '1',
        'द्वितीयकाण्डः': '2',
        'तृतीयकाण्डः': '3'
    }

    kanda_id = kanda_map.get(kanda)
    if not kanda_id:
        return None

    kanda_folder = f"Data/{kanda_id}_{kanda}"
    if not os.path.exists(kanda_folder):
        return None

    # If adhikaar is specified, look in varga subfolder
    if adhikaar:
        for item in os.listdir(kanda_folder):
            if varga in item and os.path.isdir(os.path.join(kanda_folder, item)):
                varga_folder = os.path.join(kanda_folder, item)
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
                if file_num:
                    yaml_file = os.path.join(varga_folder, f"{file_num}_{adhikaar}.yaml")
                    if os.path.exists(yaml_file):
                        return yaml_file
    else:
        # Regular varga file
        for item in os.listdir(kanda_folder):
            if varga in item and item.endswith('.yaml'):
                yaml_file = os.path.join(kanda_folder, item)
                if os.path.exists(yaml_file):
                    return yaml_file

    return None


def test_multiple_dhatu_ids_backport():
    """Test backporting for multiple_dhatu_ids files"""
    print("\n" + "="*70)
    print("TEST 1: Multiple Dhatu IDs Backport")
    print("="*70)

    test_file = "Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati/part_01.yaml"
    backup_file = test_file + ".test_backup"

    print(f"\n1️⃣  Loading test file: {test_file}")
    split_data = load_yaml_file(test_file)

    # Get first entry
    first_key = list(split_data.keys())[0]
    first_entry = split_data[first_key]

    print(f"   Entry: {first_key}")
    print(f"   Original dhatu_ids: {first_entry['dhatu_ids']}")
    print(f"   Location: {first_entry['kanda']} / {first_entry['varga']}")

    # Find the Data file
    data_file = find_data_yaml_file(
        first_entry['kanda'],
        first_entry['varga'],
        first_entry.get('adhikaar', '')
    )

    if not data_file:
        print(f"   ❌ Could not find Data file!")
        return False

    print(f"   📁 Data file: {data_file}")

    # Backup both files
    shutil.copy2(test_file, backup_file)
    data_backup = data_file + ".test_backup"
    shutil.copy2(data_file, data_backup)

    # Make a test change (select first dhatu_id only)
    original_dhatu_ids = first_entry['dhatu_ids']
    test_dhatu_id = original_dhatu_ids.split(',')[0].strip()

    print(f"\n2️⃣  Making test change...")
    print(f"   Changing '{original_dhatu_ids}' → '{test_dhatu_id}'")

    split_data[first_key]['dhatu_ids'] = test_dhatu_id
    write_yaml_file(test_file, split_data)

    # Run backport
    print(f"\n3️⃣  Running backport script...")
    os.system(f"python3 Scripts/AI_Generated/scripts/backportMultipleDhatuIds.py {test_file} Data > /tmp/backport_test.log 2>&1")

    # Verify the change in Data file
    print(f"\n4️⃣  Verifying change in Data file...")
    data_yaml = load_yaml_file(data_file)

    # Find the entry in Data file
    shloka_text = first_entry['shloka_text']
    artha = first_entry['artha']
    form = first_entry['form']

    found = False
    for shloka_key, shloka_data in data_yaml.items():
        if isinstance(shloka_data, dict) and artha in shloka_data:
            if isinstance(shloka_data[artha], dict) and form in shloka_data[artha]:
                current_value = shloka_data[artha][form]
                print(f"   Found in Data: {form}")
                print(f"   Current value in Data: {current_value}")

                # Check if it matches our test change
                if isinstance(current_value, list) and len(current_value) > 0:
                    if current_value[-1] == test_dhatu_id or current_value[0] == test_dhatu_id:
                        print(f"   ✅ Change successfully backported!")
                        found = True
                    else:
                        print(f"   ❌ Value doesn't match expected: {test_dhatu_id}")
                break

    # Restore original files
    print(f"\n5️⃣  Restoring original files...")
    shutil.move(backup_file, test_file)
    shutil.move(data_backup, data_file)
    print(f"   ✅ Files restored")

    return found


def test_not_found_backport():
    """Test backporting for not_found_dhatu_ids files"""
    print("\n" + "="*70)
    print("TEST 2: Not Found Dhatu IDs Backport")
    print("="*70)

    test_file = "Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati/part_01.yaml"
    backup_file = test_file + ".test_backup"

    print(f"\n1️⃣  Loading test file: {test_file}")
    split_data = load_yaml_file(test_file)

    # Get first entry
    first_key = list(split_data.keys())[0]
    first_entry = split_data[first_key]

    print(f"   Entry: {first_key}")
    print(f"   Original dhatu_id: {first_entry['dhatu_id']}")
    print(f"   Location: {first_entry['kanda']} / {first_entry['varga']}")

    # Find the Data file
    data_file = find_data_yaml_file(
        first_entry['kanda'],
        first_entry['varga'],
        first_entry.get('adhikaar', '')
    )

    if not data_file:
        print(f"   ❌ Could not find Data file!")
        return False

    print(f"   📁 Data file: {data_file}")

    # Backup both files
    shutil.copy2(test_file, backup_file)
    data_backup = data_file + ".test_backup"
    shutil.copy2(data_file, data_backup)

    # Make a test change (replace "Not Found" with test ID)
    test_dhatu_id = "99.9999"

    print(f"\n2️⃣  Making test change...")
    print(f"   Changing 'Not Found' → '{test_dhatu_id}'")

    split_data[first_key]['dhatu_id'] = test_dhatu_id
    write_yaml_file(test_file, split_data)

    # Run backport
    print(f"\n3️⃣  Running backport script...")
    os.system(f"python3 Scripts/AI_Generated/scripts/backportNotFoundDhatuIds.py {test_file} Data > /tmp/backport_test2.log 2>&1")

    # Verify the change in Data file
    print(f"\n4️⃣  Verifying change in Data file...")
    data_yaml = load_yaml_file(data_file)

    # Find the entry in Data file
    artha = first_entry['artha']
    form = first_entry['form']

    found = False
    for shloka_key, shloka_data in data_yaml.items():
        if isinstance(shloka_data, dict) and artha in shloka_data:
            if isinstance(shloka_data[artha], dict) and form in shloka_data[artha]:
                current_value = shloka_data[artha][form]
                print(f"   Found in Data: {form}")
                print(f"   Current value in Data: {current_value}")

                # Check if it matches our test change
                if isinstance(current_value, list) and len(current_value) > 0:
                    if current_value[-1] == test_dhatu_id or current_value[0] == test_dhatu_id:
                        print(f"   ✅ Change successfully backported!")
                        found = True
                    else:
                        print(f"   ❌ Value doesn't match expected: {test_dhatu_id}")
                break

    # Restore original files
    print(f"\n5️⃣  Restoring original files...")
    shutil.move(backup_file, test_file)
    shutil.move(data_backup, data_file)
    print(f"   ✅ Files restored")

    return found


def main():
    """Main test function"""
    print("\n" + "="*70)
    print("COMPLETE BACKPORT WORKFLOW TEST")
    print("="*70)
    print("\nThis test will:")
    print("  1. Edit a split file")
    print("  2. Run backport script")
    print("  3. Verify change appears in Data folder")
    print("  4. Restore everything")
    print("\nNo permanent changes will be made.")

    test1_passed = test_multiple_dhatu_ids_backport()
    test2_passed = test_not_found_backport()

    print("\n" + "="*70)
    print("FINAL TEST RESULTS")
    print("="*70)

    if test1_passed:
        print("✅ TEST 1 PASSED: Multiple Dhatu IDs backport works!")
    else:
        print("❌ TEST 1 FAILED: Multiple Dhatu IDs backport issue")

    if test2_passed:
        print("✅ TEST 2 PASSED: Not Found Dhatu IDs backport works!")
    else:
        print("❌ TEST 2 FAILED: Not Found Dhatu IDs backport issue")

    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Backporting from split folders to Data folder is working correctly!")
        print("="*70 + "\n")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("="*70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
