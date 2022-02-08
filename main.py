from typing import Optional, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from schema import *
import json
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


class State(BaseModel):
    active_intent: str
    requested_slots: list
    slot_values: dict


class Frame(BaseModel):
    actions: list
    service: str
    slots: list
    state: State


class Turn(BaseModel):
    # TODO: delete Optional
    frames: Optional[List[Frame]]
    speaker: str
    turn_id: str
    utterance: str


class Dialogue(BaseModel):
    dialogue_id: str
    services: List[str]
    turns: List[Turn]


class UploadDialogue(BaseModel):
    dialogue: Dialogue
    user: str
    filename: str


schema_data = ServiceSchema()
DIR_PATH = './data'


def save_dialogue(dialogue, dir_path, file_name):
    file_name_prefix = 'dialogue_'
    file_num = int(file_name.replace(file_name_prefix, ''))

    # 檢查資料夾是否存在
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    file_path = os.path.join(dir_path, file_name)
    file_path += '.json'
    dialogue_dict = dialogue.dict()
    # 檢查檔案是否存在
    if os.path.isfile(file_path):
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)
            file_current_dialogue_id = int(data[-1]['dialogue_id'].split('_')[1])
            dialogue_id_str = '{:04d}'.format(file_current_dialogue_id + 1)
            dialogue_dict['dialogue_id'] = f'{file_num}_{dialogue_id_str}'
            data.append(dialogue_dict)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            # f.write(dialogue.json())
            dialogue_id_str = '{:04d}'.format(0)
            dialogue_dict['dialogue_id'] = f'{file_num}_{dialogue_id_str}'
            json.dump([dialogue_dict], f, ensure_ascii=False, indent=4)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/goal")
async def get_initial_user_state():
    return {"message": "User State"}


@app.post("/items")
async def create_item(item: Item):
    return item


@app.post("/dialogue")
async def create_dialogue(dialog: Dialogue):
    save_dialogue(dialog, os.path.join(DIR_PATH, 'USER'), 'test.json')
    return dialog


@app.post("/upload_dialogue")
async def upload_dialogue(dialogue: UploadDialogue):
    dialogue_data = dialogue.dict()
    save_dialogue(dialogue.dialogue, os.path.join(DIR_PATH, dialogue_data["user"]),
                  dialogue.filename)
    return dialogue


@app.get("/schema")
async def get_new_task():
    return schema_data.get_random_task()
