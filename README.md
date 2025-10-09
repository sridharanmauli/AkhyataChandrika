Repository to generate AkhyataChandrika text in a format required by astadyayi.com.

Contains
  - Data: Contains the text in the form of YAML and is divided into Khandas and vargas, similar to that of the original text. This is the only manually modified component of the repository where the text's proofreading and metaInfo for the slokas are written.
  - dictionary: input folder of the dictionary contains the files that can be loaded to GoldenDict. We have extracted the text from these files in a format that will be used by us to produce text. out folder in dictionary contains formatted YAML files. This will be used to group similar-meaning verbs after each sloka of text.
  - generated: This contains the YAML files for the aforementioned output file of the dictionary, divided into chapter wise format of text.
  - Scripts: This folder contains the scripts to create the JSON file in the format astadyayi.com uses. Use iterateDirectories.py to generate the file. Its usage is mentioned in the same file.

          
