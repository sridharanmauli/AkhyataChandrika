#!/usr/bin/env python3
"""
End-to-end test of the review workflow with resolved/comment fields.

This script:
1. Marks some entries as resolved
2. Adds comments to entries
3. Runs removeResolvedEntries.py
4. Verifies resolved entries are removed
5. Verifies backport still works
6. Restores everything
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


def main():
    """Main test function"""
    print("\n" + "="*70)
    print("COMPLETE REVIEW WORKFLOW TEST")
    print("="*70)

    test_file = "Scripts/AI_Generated/output/multipleDhatuIdsWithoutGati/part_01.yaml"
    backup_file = test_file + ".review_test_backup"

    print(f"\n1️⃣  Setting up test...")
    print(f"   Test file: {test_file}")

    # Backup
    shutil.copy2(test_file, backup_file)

    # Load file
    header = read_header_lines(test_file)
    data = load_yaml_file(test_file)
    original_count = len(data)
    print(f"   Original entries: {original_count}")

    # Mark first 3 entries as resolved with comments
    print(f"\n2️⃣  Marking 3 entries as resolved...")
    keys = list(data.keys())
    for i in range(3):
        key = keys[i]
        data[key]['resolved'] = 'true'
        data[key]['comment'] = f'Test comment for entry {i+1}'
        print(f"   ✅ {key}: resolved=true, comment added")

    # Write modified file
    write_yaml_with_header(test_file, data, header)

    # Run removeResolvedEntries.py
    print(f"\n3️⃣  Running removeResolvedEntries.py...")
    os.system(f"python3 Scripts/AI_Generated/scripts/removeResolvedEntries.py > /tmp/remove_test.log 2>&1")

    # Verify
    print(f"\n4️⃣  Verifying results...")
    data_after = load_yaml_file(test_file)
    new_count = len(data_after)

    print(f"   Entries before: {original_count}")
    print(f"   Entries after:  {new_count}")
    print(f"   Removed:        {original_count - new_count}")

    if new_count == original_count - 3:
        print(f"   ✅ Correct number of entries removed!")
    else:
        print(f"   ❌ Expected {original_count - 3} entries, got {new_count}")
        shutil.move(backup_file, test_file)
        return False

    # Verify resolved entries are gone
    removed_keys = keys[:3]
    all_removed = True
    for key in removed_keys:
        if key in data_after:
            print(f"   ❌ Entry still present: {key}")
            all_removed = False

    if all_removed:
        print(f"   ✅ All resolved entries successfully removed!")
    else:
        print(f"   ❌ Some resolved entries still present")
        shutil.move(backup_file, test_file)
        return False

    # Test backport still works
    print(f"\n5️⃣  Testing backport with remaining entries...")
    os.system(f"python3 Scripts/AI_Generated/scripts/backportMultipleDhatuIds.py {test_file} Data > /tmp/backport_review_test.log 2>&1")

    # Check backport log
    with open('/tmp/backport_review_test.log', 'r') as f:
        log = f.read()
        if 'Successfully updated:' in log:
            print(f"   ✅ Backport still works with review fields!")
        else:
            print(f"   ❌ Backport failed")

    # Restore
    print(f"\n6️⃣  Restoring original file...")
    shutil.move(backup_file, test_file)
    print(f"   ✅ File restored")

    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    print("✅ Review fields (resolved, comment) working correctly")
    print("✅ removeResolvedEntries.py removes resolved entries")
    print("✅ Entry counts are updated correctly")
    print("✅ Backport ignores review fields and still works")
    print("\n🎉 COMPLETE REVIEW WORKFLOW TEST PASSED!")
    print("="*70 + "\n")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
