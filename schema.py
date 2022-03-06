import random
import json

SCHEMA_FILE = '../schema.json'
MAX_SLOT_TURN = 2

def read_json(path):
    f = open(path, encoding='utf-8')
    data = json.load(f)
    return data


class ServiceSchema:
    def __init__(self):
        self.schema_data = read_json(SCHEMA_FILE)

    def get_random_schema(self):
        random_id = random.randint(0, len(self.schema_data) - 1)
        current_schema = self.schema_data[random_id].copy()

        # Choose random slot to delete
        n = random.randint(0, len(self.schema_data) - 2)
        to_delete = set(random.sample(range(len(current_schema['slots'])), n))
        current_schema['slots'] = [x for i, x in enumerate(current_schema['slots']) if not i in to_delete]
        random.shuffle(current_schema['slots'])

        i = 0
        result = []
        while i < len(current_schema['slots']):
            mn = random.randint(1, 2)
            item = []
            for j in range(i, i + mn):
                if j < len(current_schema['slots']):
                    item += [current_schema['slots'][j]]
            result.append(item)
            i += mn

        current_schema['slots'] = result

        return current_schema
