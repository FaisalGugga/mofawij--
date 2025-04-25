import json

def load_local_data(file_path="data/local_data.json"):
    with open(file_path, 'r') as file:
        return json.load(file)
