#!/usr/bin/env python3
import yaml
import json
import os
import sys
from generateSlokas import yaml_to_json

# ------------------------------
# Function to read mangalam from mangalam.yaml in a Kanda folder
# ------------------------------
def read_mangalam(kanda_folder):
    mangalam_file = os.path.join(kanda_folder, "mangalam.yaml")
    if not os.path.exists(mangalam_file):
        return []  # fallback to empty list if file missing
    with open(mangalam_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    # Each key in the YAML becomes a line in mangalam
    return [line.strip().rstrip(':') for line in data.keys()]

# ------------------------------
# Function to extract vargas for a given Kanda folder
# ------------------------------
def extract_varga_data(varga_folder):
    vargas = []
    for file_name in sorted(os.listdir(varga_folder)):
        if file_name.endswith('.yaml') and file_name != 'mangalam.yaml':
            varga_id = int(file_name.split('_')[0])
            varga_name = '_'.join(file_name.split('_')[1:]).replace('.yaml','')
            yaml_file = os.path.join(varga_folder, file_name)
            shlokas_json = yaml_to_json(yaml_file)
            vargas.append({
                "varga_id": varga_id,
                "varga_name": varga_name,
                "shlokas": shlokas_json["shlokas"]
            })
    return vargas

# ------------------------------
# Main function to generate the full JSON
# ------------------------------
def generate_full_json(data_folder):
    data = []
    for kanda_name in sorted(os.listdir(data_folder)):
        kanda_path = os.path.join(data_folder, kanda_name)
        if os.path.isdir(kanda_path):
            kanda_id = int(kanda_name.split('_')[0])
            kanda_display_name = '_'.join(kanda_name.split('_')[1:])
            mangalam_lines = read_mangalam(kanda_path)
            vargas = extract_varga_data(kanda_path)
            data.append({
                "kanda_id": kanda_id,
                "kanda_name": kanda_display_name,
                "mangalam": mangalam_lines,
                "vargas": vargas
            })
    return {"data": sorted(data, key=lambda x: x["kanda_id"])}

# ------------------------------
# Script execution
# ------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 generate_full_json.py <Data_Folder> <Output_JSON>")
        sys.exit(1)

    data_folder = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(data_folder):
        print(f"Error: {data_folder} does not exist")
        sys.exit(1)

    full_json = generate_full_json(data_folder)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_json, f, ensure_ascii=False, indent=4)

    print(f"✅ Full JSON written to {output_file}")

