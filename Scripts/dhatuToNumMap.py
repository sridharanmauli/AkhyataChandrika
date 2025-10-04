import json

# Take DhatuForms from website.  
# https://github.com/ashtadhyayi-com/data/blob/master/dhatu/dhatuforms_vidyut_shuddha_kartari.txt
# Read the txt file
with open("../Data/DhatuForms.txt", "r", encoding="utf-8") as f:
    txt_data = f.read()

# Convert text to JSON
data = json.loads(txt_data)

mapping = {}

for number, forms in data.items():
    for key, value in forms.items():
        if key == "plat" or key == "alat":
         # Take the first form from each semicolon-separated string
         first_form = value.split(";")[0]
         # Add to mapping (overwriting duplicates is fine since same number)
         mapping[first_form] = number

# Save mapping to JSON
with open("mapping.json", "w", encoding="utf-8") as f:
    json.dump(mapping, f, ensure_ascii=False, indent=2)

print("Mapping for all first forms created successfully!")
