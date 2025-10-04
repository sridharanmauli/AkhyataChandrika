This powers the Data for AkhyataChandrika in a format required for ashtadhyayi.com. 
We are manually writing Yaml files and some scripts to convert this yaml files to JsonFile required
by the website.

Final File will be present in Scripts/outputJson.json. 

Run 
python3 iterateDirectories.py ../Data/ outputJson.json from Scripts folder to get this output.

Scripts iterate all folders and populate appropriate Json attributes along with parsing the yaml files.
