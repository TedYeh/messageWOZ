import random
import json

SCHEMA_FILE = 'schema.json'


def read_json(path):
    f = open(path, encoding='utf-8')
    data = json.load(f)
    return data


class ServiceSchema:
    def __init__(self):
        self.schema_data = read_json(SCHEMA_FILE)

    def get_random_task(self):
        random_id = random.randint(0, len(self.schema_data) - 1)
        current_schema = self.schema_data[random_id].copy()

        # Choose random slot to delete
        n = random.randint(0, len(self.schema_data) - 2)
        to_delete = set(random.sample(range(len(current_schema['slots'])), n))
        current_schema['slots'] = [x for i, x in enumerate(current_schema['slots']) if not i in to_delete]
        # random.shuffle(current_schema['slots'])
        new_slots = []
        for i, slot in enumerate(current_schema['slots']):
            if i not in to_delete:
                if slot['is_categorical']:
                    slot['possible_values'] = [random.choice(slot['possible_values'])]
                new_slots.append(slot)

        return current_schema
