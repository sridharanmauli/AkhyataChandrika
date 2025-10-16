#!/usr/bin/env python3
"""
Comprehensive verification of:
1. Entries with resolved=true are deleted from generated files
2. Backporting still works correctly with review fields
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


def read_header_lines(yaml_file):
    """Read header lines"""
    header_lines = []
    with open(yaml_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'):
                header_lines.append(line.rstrip())
            elif line.strip():
                break
    return header_lines


def write_yaml_with_header(yaml_file, data, header_lines):
    """Write YAML with header"""
    with open(yaml_file, 'w', encoding='utf-8') as f:
        for line in header_lines:
            f.write(f"{line}\n")
        f.write("\n")
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False,
                  indent=2, sort_keys=False, width=1000, Dumper=QuotedDumper)


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

    if adhikaar:
        for item in os.listdir(kanda_folder):
            if varga in item and os.path.isdir(os.path.join(kanda_folder, item)):
                varga_folder = os.path.join(kanda_folder, item)
                adhikaar_to_file = {
                    'भ्वादिगणः': '1', 'अदादिगणः': '2', 'जुहोत्यादिगणः': '3',
                    'दिवादिगणः': '4', 'स्वादिगणः': '5', 'तुदादिगणः': '6',
                    'रुधादिगणः': '7', 'तनादिगणः': '8', 'क्रयादिगणः': '9',
                    'चुरादिगणः': '10', 'नामधातवः': '11', 'कण्ड्वादयः': '12'
                }
                file_num = adhikaar_to_file.get(adhikaar)
                if file_num:
                    yaml_file = os.path.join(varga_folder, f"{file_num}_{adhikaar}.yaml")
                    if os.path.exists(yaml_file):
                        return yaml_file
    else:
        for item in os.listdir(kanda_folder):
            if varga in item and item.endswith('.yaml'):
                yaml_file = os.path.join(kanda_folder, item)
                if os.path.exists(yaml_file):
                    return yaml_file
    return None


def test_resolved_deletion():
    """Test that entries with resolved=true are deleted"""
    print("\n" + "="*70)
    print("TEST 1: VERIFY RESOLVED ENTRIES ARE DELETED")
    print("="*70)

    test_file = "Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati/part_02.yaml"
    backup_file = test_file + ".deletion_test_backup"

    print(f"\n1️⃣  Setting up test with {test_file}")

    # Backup
    shutil.copy2(test_file, backup_file)

    # Load file
    header = read_header_lines(test_file)
    data = load_yaml_file(test_file)
    original_count = len(data)
    print(f"   Original entries: {original_count}")

    # Mark 5 specific entries as resolved
    keys = list(data.keys())
    entries_to_resolve = keys[:5]

    print(f"\n2️⃣  Marking 5 entries as resolved=true:")
    for i, key in enumerate(entries_to_resolve, 1):
        data[key]['resolved'] = 'true'
        data[key]['comment'] = f'Test resolution {i}'
        print(f"   {i}. {key}")

    # Write modified file
    write_yaml_with_header(test_file, data, header)

    # Run removeResolvedEntries.py
    print(f"\n3️⃣  Running removeResolvedEntries.py...")
    exit_code = os.system(f"python3 Scripts/AI_Generated/scripts/removeResolvedEntries.py > /tmp/deletion_test.log 2>&1")

    if exit_code != 0:
        print(f"   ❌ Script failed with exit code {exit_code}")
        shutil.move(backup_file, test_file)
        return False

    # Verify entries are deleted
    print(f"\n4️⃣  Verifying entries are deleted...")
    data_after = load_yaml_file(test_file)
    new_count = len(data_after)

    print(f"   Entries before: {original_count}")
    print(f"   Entries after:  {new_count}")
    print(f"   Expected:       {original_count - 5}")

    if new_count != original_count - 5:
        print(f"   ❌ FAILED: Expected {original_count - 5} entries, got {new_count}")
        shutil.move(backup_file, test_file)
        return False

    # Verify specific entries are gone
    print(f"\n5️⃣  Checking that resolved entries are actually deleted:")
    all_deleted = True
    for key in entries_to_resolve:
        if key in data_after:
            print(f"   ❌ Entry still exists: {key}")
            all_deleted = False
        else:
            print(f"   ✅ Deleted: {key}")

    # Restore
    print(f"\n6️⃣  Restoring original file...")
    shutil.move(backup_file, test_file)

    if all_deleted:
        print(f"\n✅ TEST 1 PASSED: All resolved entries successfully deleted!")
        return True
    else:
        print(f"\n❌ TEST 1 FAILED: Some resolved entries not deleted!")
        return False


def test_backporting_with_review_fields():
    """Test that backporting works with resolved and comment fields"""
    print("\n" + "="*70)
    print("TEST 2: VERIFY BACKPORTING WORKS WITH REVIEW FIELDS")
    print("="*70)

    # Test both multiple_dhatu_ids and not_found
    test_file1 = "Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati/part_03.yaml"
    test_file2 = "Scripts/AI_Generated/output/notFoundDhatuIdsWithoutGati/part_02.yaml"

    backup_file1 = test_file1 + ".backport_test_backup"
    backup_file2 = test_file2 + ".backport_test_backup"

    print(f"\n1️⃣  Testing backport for Multiple Dhatu IDs...")
    print(f"   Test file: {test_file1}")

    # Backup
    shutil.copy2(test_file1, backup_file1)

    # Load and modify
    header1 = read_header_lines(test_file1)
    data1 = load_yaml_file(test_file1)

    first_key = list(data1.keys())[0]
    first_entry = data1[first_key]

    print(f"   Entry: {first_key}")
    print(f"   Original dhatu_ids: {first_entry['dhatu_ids']}")
    print(f"   Has resolved field: {'resolved' in first_entry}")
    print(f"   Has comment field: {'comment' in first_entry}")

    # Make a change and add review fields
    original_dhatu_ids = first_entry['dhatu_ids']
    test_dhatu_id = original_dhatu_ids.split(',')[0].strip()
    data1[first_key]['dhatu_ids'] = test_dhatu_id
    data1[first_key]['resolved'] = 'false'  # Not resolved
    data1[first_key]['comment'] = 'Test backport with review fields'

    write_yaml_with_header(test_file1, data1, header1)

    # Find Data file to backup
    data_file = find_data_yaml_file(
        first_entry['kanda'],
        first_entry['varga'],
        first_entry.get('adhikaar', '')
    )

    if not data_file:
        print(f"   ❌ Could not find Data file")
        shutil.move(backup_file1, test_file1)
        return False

    data_backup = data_file + ".backport_test_backup"
    shutil.copy2(data_file, data_backup)

    # Run backport
    print(f"\n2️⃣  Running backport script...")
    exit_code = os.system(f"python3 Scripts/AI_Generated/scripts/backportMultipleDhatuIds.py {test_file1} Data > /tmp/backport_test1.log 2>&1")

    if exit_code != 0:
        print(f"   ❌ Backport failed with exit code {exit_code}")
        shutil.move(backup_file1, test_file1)
        shutil.move(data_backup, data_file)
        return False

    # Verify change in Data file
    print(f"\n3️⃣  Verifying change in Data file...")
    data_yaml = load_yaml_file(data_file)

    artha = first_entry['artha']
    form = first_entry['form']

    found = False
    for shloka_key, shloka_data in data_yaml.items():
        if isinstance(shloka_data, dict) and artha in shloka_data:
            if isinstance(shloka_data[artha], dict) and form in shloka_data[artha]:
                current_value = shloka_data[artha][form]
                print(f"   Found in Data: {form}")
                print(f"   Value in Data: {current_value}")

                if isinstance(current_value, list) and len(current_value) > 0:
                    if current_value[-1] == test_dhatu_id or current_value[0] == test_dhatu_id:
                        print(f"   ✅ Change successfully backported!")
                        found = True
                break

    # Restore files
    print(f"\n4️⃣  Restoring files...")
    shutil.move(backup_file1, test_file1)
    shutil.move(data_backup, data_file)

    # Test not_found backport
    print(f"\n5️⃣  Testing backport for Not Found Dhatu IDs...")
    print(f"   Test file: {test_file2}")

    shutil.copy2(test_file2, backup_file2)

    header2 = read_header_lines(test_file2)
    data2 = load_yaml_file(test_file2)

    second_key = list(data2.keys())[0]
    second_entry = data2[second_key]

    print(f"   Entry: {second_key}")
    print(f"   Original dhatu_id: {second_entry['dhatu_id']}")

    # Change to test ID
    test_dhatu_id2 = "88.8888"
    data2[second_key]['dhatu_id'] = test_dhatu_id2
    data2[second_key]['resolved'] = 'true'  # Marked as resolved
    data2[second_key]['comment'] = 'Another test with resolved=true'

    write_yaml_with_header(test_file2, data2, header2)

    # Find Data file
    data_file2 = find_data_yaml_file(
        second_entry['kanda'],
        second_entry['varga'],
        second_entry.get('adhikaar', '')
    )

    if not data_file2:
        print(f"   ❌ Could not find Data file")
        shutil.move(backup_file2, test_file2)
        return found

    data_backup2 = data_file2 + ".backport_test_backup2"
    shutil.copy2(data_file2, data_backup2)

    # Run backport
    print(f"\n6️⃣  Running backport script...")
    exit_code = os.system(f"python3 Scripts/AI_Generated/scripts/backportNotFoundDhatuIds.py {test_file2} Data > /tmp/backport_test2.log 2>&1")

    # Verify change
    print(f"\n7️⃣  Verifying change in Data file...")
    data_yaml2 = load_yaml_file(data_file2)

    artha2 = second_entry['artha']
    form2 = second_entry['form']

    found2 = False
    for shloka_key, shloka_data in data_yaml2.items():
        if isinstance(shloka_data, dict) and artha2 in shloka_data:
            if isinstance(shloka_data[artha2], dict) and form2 in shloka_data[artha2]:
                current_value = shloka_data[artha2][form2]
                print(f"   Found in Data: {form2}")
                print(f"   Value in Data: {current_value}")

                if isinstance(current_value, list) and len(current_value) > 0:
                    if current_value[-1] == test_dhatu_id2 or current_value[0] == test_dhatu_id2:
                        print(f"   ✅ Change successfully backported (even with resolved=true)!")
                        found2 = True
                break

    # Restore
    print(f"\n8️⃣  Restoring files...")
    shutil.move(backup_file2, test_file2)
    shutil.move(data_backup2, data_file2)

    if found and found2:
        print(f"\n✅ TEST 2 PASSED: Backporting works correctly with review fields!")
        return True
    else:
        print(f"\n❌ TEST 2 FAILED: Backporting issue detected!")
        return False


def main():
    """Run all verification tests"""
    print("\n" + "="*70)
    print("COMPREHENSIVE VERIFICATION")
    print("Testing: Entry Deletion and Backporting")
    print("="*70)

    test1_passed = test_resolved_deletion()
    test2_passed = test_backporting_with_review_fields()

    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)

    if test1_passed:
        print("✅ TEST 1 PASSED: Resolved entries are deleted correctly")
    else:
        print("❌ TEST 1 FAILED: Issue with deleting resolved entries")

    if test2_passed:
        print("✅ TEST 2 PASSED: Backporting works with review fields")
    else:
        print("❌ TEST 2 FAILED: Issue with backporting")

    print("="*70)

    if test1_passed and test2_passed:
        print("\n🎉 ALL VERIFICATION TESTS PASSED!")
        print("="*70 + "\n")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED - Please review above")
        print("="*70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
