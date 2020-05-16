import settings
import json

with open('translation_data.json', encoding='utf-8') as file:
    all_translations = json.load(file)

translate_collection = settings.get_collection('Translation')
translate_collection.insert_many(all_translations)