from os import listdir, path
from os.path import isfile, join

import json

import settings
import db_module


def load_file(file_path: str):

    with open(file_path, encoding="UTF-8") as f:
        data = json.load(f)

        assert 'collection' in data.keys(), 'COLLECTION field is not defined'
        assert 'entries' in data.keys(), 'ENTRIES field is not defined'

        collection = data['collection']
        assert collection in settings.UploadCollections, f'collection {collection} is not allowed to upload'

        entries = data['entries']
        db_module.insert_entries(collection, entries=entries)
        print('\n*******')
        print(f"Uploaded: {file_path}")

    return


data_folder = path.dirname(__file__) + './data/'
all_files = [data_folder + f for f in listdir(data_folder) if isfile(join(data_folder, f))]

for file in all_files:
    try:
        load_file(file)
    except Exception as e:
        print('\n*******')
        print(f"{file}: failed to load file - {e}")