import requests
import json

# URL of the raw text file on GitHub
url = "https://raw.githubusercontent.com/ashtadhyayi-com/data/master/dhatu/dhatuforms_vidyut_shuddha_kartari.txt"

# Fetch the content
response = requests.get(url)
response.raise_for_status()  # Raise an exception for HTTP errors

# Read the content as text
txt_data = response.text

# Convert the text to JSON
data = json.loads(txt_data)

# Convert text to JSON
data = json.loads(txt_data)

mapping = {}

for number, forms in data.items():
    for key, value in forms.items():
        if key == "plat" or key == "alat":
            # Take the first form from semicolon-separated string
            first_form = value.split(";")[0]
            
            # Split by comma if multiple forms are present
            first_forms = [f.strip() for f in first_form.split(",")]
            
            # Add each to mapping
            for f in first_forms:
                if f not in mapping:  # Avoid overwriting existing entries
                    mapping[f] = number
                else:
                    mapping[f] += f", {number}"

# Save mapping to JSON
with open("output/mapping.json", "w", encoding="utf-8") as f:
    json.dump(mapping, f, ensure_ascii=False, indent=2)

print("Mapping for all first forms created successfully!")
