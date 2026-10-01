import json
import os

class Storage:
    def __init__(self, file_path="students.json"):
        self.file_path = file_path

    def save(self, data):
        with open(self.file_path, 'w') as f:
            json.dump(data, f)

    def load(self):
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, 'r') as f:
            return json.load(f)