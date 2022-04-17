import json


class JsonManager():
        json_object: dict = None
        filename: str = None
        
        def __init__(self, filename):
                self.filename = filename
                with open(filename, 'r', encoding='utf8') as file:
                        self.json_object = json.load(file)
        def save(self):
                with open(self.filename, 'w') as file:
                        json.dump(self.json_object, file, indent=4)

