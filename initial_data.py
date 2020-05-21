import settings
import json

files = ['Courses', 'Translation']

for file in files:
    file_name = file+'.json'
    with open(file_name, encoding='utf-8') as f:
        all_entries = json.load(f)

    collection = settings.get_collection(file)
    collection.insert_many(all_entries)