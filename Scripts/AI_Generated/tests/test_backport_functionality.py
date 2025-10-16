#!/usr/bin/env python3
"""
Comprehensive test script to verify backport functionality works correctly.

This script:
1. Creates a small test YAML file with a few entries
2. Backs up original YAML files that will be modified
3. Runs the backport script
4. Verifies the changes were applied correctly
5. Restores original files
"""

import yaml
import os
import shutil
import json
from collections import OrderedDict

# Custom YAML dumper (same as in collectMultipleDhatuIds.py)
class QuotedDumper(yaml.SafeDumper):
    pass

def quoted_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

def ordered_dict_representer(dumper, data):
    return dumper.represent_dict(data.items())

yaml.add_representer(str, quoted_str_representer, Dumper=QuotedDumper)
yaml.add_representer(OrderedDict, ordered_dict_representer, Dumper=QuotedDumper)

# Custom YAML loader
class ForceStringLoader(yaml.SafeLoader):
    pass

def str_constructor(loader, node):
    return loader.construct_scalar(node)

def dict_constructor(loader, node):
    return OrderedDict(loader.construct_pairs(node))

ForceStringLoader.add_constructor(u'tag:yaml.org,2002:int', str_constructor)
ForceStringLoader.add_constructor(u'tag:yaml.org,2002:float', str_constructor)
ForceStringLoader.add_constructor(u'tag:yaml.org,2002:map', dict_constructor)


def create_test_file():
    """Create a small test YAML file with a few sample entries"""

    # Read the actual generated files to get real test cases
    test_cases_without_gati = []
    test_cases_with_gati = []

    # Get 3 test cases from each file
    without_gati_file = "Scripts/output/multiple_dhatu_ids_without_gati.yaml"
    with_gati_file = "Scripts/output/multiple_dhatu_ids_with_gati.yaml"

    if os.path.exists(without_gati_file):
        with open(without_gati_file, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=ForceStringLoader)
            count = 0
            for key, value in data.items():
                if count < 3:
                    test_cases_without_gati.append((key, value))
                    count += 1
                else:
                    break

    if os.path.exists(with_gati_file):
        with open(with_gati_file, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=ForceStringLoader)
            count = 0
            for key, value in data.items():
                if count < 3:
                    test_cases_with_gati.append((key, value))
                    count += 1
                else:
                    break

    return test_cases_without_gati, test_cases_with_gati


def create_test_yaml_files(test_cases_without_gati, test_cases_with_gati):
    """Create test YAML files with modified dhatu_ids"""

    # Create test directory
    test_dir = "Scripts/test_output"
    os.makedirs(test_dir, exist_ok=True)

    # For WITHOUT gati file - modify the first entry
    if test_cases_without_gati:
        test_data = OrderedDict()
        for i, (key, value) in enumerate(test_cases_without_gati):
            if i == 0:
                # Modify the dhatu_ids - take only the first ID
                modified_value = value.copy()
                dhatu_ids = value.get('dhatu_ids', '')
                if ',' in dhatu_ids:
                    # Take only the first ID
                    first_id = dhatu_ids.split(',')[0].strip()
                    modified_value['dhatu_ids'] = first_id
                    print(f"Test case 1 (without gati): {key}")
                    print(f"  Original: {dhatu_ids}")
                    print(f"  Modified: {first_id}")
                test_data[key] = modified_value
            else:
                test_data[key] = value

        # Write test file (must match naming pattern expected by backport script)
        test_file_without = os.path.join(test_dir, "multiple_dhatu_ids_without_gati.yaml")
        with open(test_file_without, 'w', encoding='utf-8') as f:
            f.write("# Test file for backport verification\n\n")
            yaml.dump(test_data, f, allow_unicode=True, default_flow_style=False,
                     indent=2, sort_keys=False, width=1000, Dumper=QuotedDumper)

    # For WITH gati file - modify the first entry
    if test_cases_with_gati:
        test_data = OrderedDict()
        for i, (key, value) in enumerate(test_cases_with_gati):
            if i == 0:
                # Modify the dhatu_ids - take only the first ID
                modified_value = value.copy()
                dhatu_ids = value.get('dhatu_ids', '')
                if ',' in dhatu_ids:
                    # Take only the first ID
                    first_id = dhatu_ids.split(',')[0].strip()
                    modified_value['dhatu_ids'] = first_id
                    print(f"\nTest case 2 (with gati): {key}")
                    print(f"  Original: {dhatu_ids}")
                    print(f"  Modified: {first_id}")
                test_data[key] = modified_value
            else:
                test_data[key] = value

        # Write test file (must match naming pattern expected by backport script)
        test_file_with = os.path.join(test_dir, "multiple_dhatu_ids_with_gati.yaml")
        with open(test_file_with, 'w', encoding='utf-8') as f:
            f.write("# Test file for backport verification\n\n")
            yaml.dump(test_data, f, allow_unicode=True, default_flow_style=False,
                     indent=2, sort_keys=False, width=1000, Dumper=QuotedDumper)

    return test_file_without if test_cases_without_gati else None, \
           test_file_with if test_cases_with_gati else None


def backup_original_files(test_cases_without_gati, test_cases_with_gati):
    """Backup original YAML files that will be modified"""

    backups = []

    # Get the files that will be affected
    all_test_cases = test_cases_without_gati + test_cases_with_gati

    for key, value in all_test_cases:
        kanda = value.get('kanda')
        varga = value.get('varga')
        adhikaar = value.get('adhikaar')

        # Find the file path
        from backportMultipleDhatuIds import find_yaml_file
        yaml_file = find_yaml_file('Data', kanda, varga, adhikaar if adhikaar else None)

        if yaml_file and os.path.exists(yaml_file):
            # Create backup
            backup_file = yaml_file + '.backup_test'
            shutil.copy2(yaml_file, backup_file)
            backups.append((yaml_file, backup_file))
            print(f"\n✅ Backed up: {yaml_file}")

    return backups


def verify_backport(test_cases_without_gati, test_cases_with_gati):
    """Verify that the backport was applied correctly"""

    print("\n" + "="*70)
    print("VERIFICATION: Checking if changes were applied correctly")
    print("="*70)

    all_test_cases = []
    if test_cases_without_gati:
        all_test_cases.append(('without_gati', test_cases_without_gati[0]))
    if test_cases_with_gati:
        all_test_cases.append(('with_gati', test_cases_with_gati[0]))

    verification_passed = True

    for test_type, (key, value) in all_test_cases:
        form = value.get('form')
        expected_dhatu_id = value.get('dhatu_ids').split(',')[0].strip()
        gati = value.get('gati', '')
        kanda = value.get('kanda')
        varga = value.get('varga')
        adhikaar = value.get('adhikaar')
        artha = value.get('artha')
        shloka_text = value.get('shloka_text')

        print(f"\n📋 Test Case ({test_type}): {key}")
        print(f"   Expected dhatu_id: {expected_dhatu_id}")

        # Find and read the original file
        from backportMultipleDhatuIds import find_yaml_file
        yaml_file = find_yaml_file('Data', kanda, varga, adhikaar if adhikaar else None)

        if not yaml_file:
            print(f"   ❌ FAIL: Could not find YAML file")
            verification_passed = False
            continue

        # Read the file
        with open(yaml_file, 'r', encoding='utf-8') as f:
            yaml_data = yaml.load(f, Loader=ForceStringLoader)

        # Find the verb in the YAML data
        found = False
        actual_value = None

        for shloka_key in yaml_data.keys():
            if shloka_text.strip() in shloka_key or shloka_key.strip() in shloka_text:
                shloka_data = yaml_data[shloka_key]

                if shloka_data and isinstance(shloka_data, dict):
                    if artha in shloka_data:
                        artha_data = shloka_data[artha]

                        if isinstance(artha_data, dict) and form in artha_data:
                            actual_value = artha_data[form]
                            found = True
                            break

        if not found:
            print(f"   ❌ FAIL: Could not find verb '{form}' in YAML file")
            verification_passed = False
            continue

        # Check the value
        if actual_value is None:
            print(f"   ❌ FAIL: Verb has null value")
            verification_passed = False
            continue

        # Extract dhatu_id from the actual value
        if isinstance(actual_value, list):
            if gati and gati.strip():
                # Format: [gati, dhatu_id]
                if len(actual_value) >= 2:
                    actual_dhatu_id = actual_value[1]
                else:
                    print(f"   ❌ FAIL: Expected [gati, dhatu_id] format, got {actual_value}")
                    verification_passed = False
                    continue
            else:
                # Format: [dhatu_id]
                if len(actual_value) >= 1:
                    actual_dhatu_id = actual_value[0]
                else:
                    print(f"   ❌ FAIL: Expected [dhatu_id] format, got {actual_value}")
                    verification_passed = False
                    continue
        else:
            print(f"   ❌ FAIL: Expected list format, got {type(actual_value)}")
            verification_passed = False
            continue

        # Compare
        if actual_dhatu_id == expected_dhatu_id:
            print(f"   ✅ PASS: dhatu_id correctly updated to '{actual_dhatu_id}'")
            print(f"   File: {yaml_file}")
        else:
            print(f"   ❌ FAIL: dhatu_id mismatch")
            print(f"      Expected: {expected_dhatu_id}")
            print(f"      Actual:   {actual_dhatu_id}")
            verification_passed = False

    return verification_passed


def restore_backups(backups):
    """Restore original files from backups"""

    print("\n" + "="*70)
    print("CLEANUP: Restoring original files")
    print("="*70)

    for original_file, backup_file in backups:
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, original_file)
            os.remove(backup_file)
            print(f"✅ Restored: {original_file}")


def main():
    print("="*70)
    print("BACKPORT FUNCTIONALITY TEST")
    print("="*70)

    # Step 1: Create test cases
    print("\n📥 Step 1: Loading test cases...")
    test_cases_without_gati, test_cases_with_gati = create_test_file()

    if not test_cases_without_gati and not test_cases_with_gati:
        print("❌ Error: Could not load test cases")
        return False

    print(f"✅ Loaded {len(test_cases_without_gati)} test cases without gati")
    print(f"✅ Loaded {len(test_cases_with_gati)} test cases with gati")

    # Step 2: Create test YAML files
    print("\n📝 Step 2: Creating test YAML files...")
    test_file_without, test_file_with = create_test_yaml_files(
        test_cases_without_gati, test_cases_with_gati
    )

    # Step 3: Backup original files
    print("\n💾 Step 3: Backing up original files...")
    backups = backup_original_files(test_cases_without_gati, test_cases_with_gati)

    if not backups:
        print("❌ Error: Could not create backups")
        return False

    print(f"✅ Created {len(backups)} backup(s)")

    # Step 4: Run backport script
    print("\n🔄 Step 4: Running backport script...")
    import subprocess

    try:
        # Run backport on test directory
        result = subprocess.run(
            ['python3', 'Scripts/backportMultipleDhatuIds.py', 'Scripts/test_output', 'Data'],
            capture_output=True,
            text=True,
            timeout=60
        )

        print("Backport output:")
        print(result.stdout)

        if result.returncode != 0:
            print(f"❌ Backport script failed with return code {result.returncode}")
            print(f"Error output:\n{result.stderr}")
            restore_backups(backups)
            return False

        print("✅ Backport script completed successfully")

    except Exception as e:
        print(f"❌ Error running backport script: {e}")
        restore_backups(backups)
        return False

    # Step 5: Verify changes
    print("\n🔍 Step 5: Verifying changes...")
    verification_passed = verify_backport(test_cases_without_gati, test_cases_with_gati)

    # Step 6: Restore backups
    restore_backups(backups)

    # Step 7: Cleanup test files
    print("\n🧹 Step 7: Cleaning up test files...")
    if test_file_without and os.path.exists(test_file_without):
        os.remove(test_file_without)
    if test_file_with and os.path.exists(test_file_with):
        os.remove(test_file_with)

    # Try to remove test directory if empty
    try:
        os.rmdir('Scripts/test_output')
        print("✅ Removed test directory")
    except:
        pass

    # Final result
    print("\n" + "="*70)
    if verification_passed:
        print("✅ ✅ ✅  ALL TESTS PASSED  ✅ ✅ ✅")
        print("="*70)
        print("\nBackport functionality is working correctly!")
        print("You can safely use the scripts to process the actual data.")
        return True
    else:
        print("❌ ❌ ❌  TESTS FAILED  ❌ ❌ ❌")
        print("="*70)
        print("\nBackport functionality has issues that need to be fixed.")
        print("DO NOT use the scripts on actual data until issues are resolved.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
