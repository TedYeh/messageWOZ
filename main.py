from fastapi import (
    FastAPI, WebSocket, WebSocketDisconnect, Request, Response
)
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from schema import *
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os
import uvicorn
import glob

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
# -------------------websocket 多人連線對話部分-------------------
# locate templates
templates = Jinja2Templates(directory="templates")
schema_data = ServiceSchema()

class RegisterValidator(BaseModel): # 接收使用者名稱用
    username: str

    class Config:
        orm_mode = True

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

@app.get("/") # 主頁(登入頁面)，選擇你要擔任的腳色(SYSTEM、USER)
def get_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/chat") # 聊天頁面，目前已將原index.html做整合
def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/api/current_user") # 確認目前腳色是SYSTEM or USER
def get_user(request: Request):
    return request.cookies.get("X-Authorization")

@app.get("/schema") # sent multi-domain slot
async def get_new_task():
    return schema_data.get_random_schemas()
    #return schema_data.get_random_schema()

@app.post("/upload_dialogue")
async def upload_dialogue(dialogue: UploadDialogue):
    dialogue_data = dialogue.dict()
    save_dialogue(dialogue.dialogue, os.path.join(DIR_PATH, dialogue_data["user"]),
                  dialogue.filename)
    return dialogue

@app.post("/api/register") # 在home.html使用而已，做腳色註冊用
def register_user(user: RegisterValidator, response: Response):
    response.set_cookie(key="X-Authorization", value=user.username, httponly=True)

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

class SocketManager: # websocket，多人連線對話用
    def __init__(self):
        self.active_connections: List[(WebSocket, str)] = []

    async def connect(self, websocket: WebSocket, user: str):
        await websocket.accept()
        self.active_connections.append((websocket, user))

    def disconnect(self, websocket: WebSocket, user: str):
        self.active_connections.remove((websocket, user))

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            await connection[0].send_json(data)


manager = SocketManager()


@app.websocket("/api/chat") # 使用websocket做廣播，將訊息傳給所有使用者
async def chat(websocket: WebSocket):
    sender = websocket.cookies.get("X-Authorization")
    if sender:
        await manager.connect(websocket, sender)
        response = {
            "sender": sender, # sender: SYSTEM or USER
            "message": "got connected"
        }
        await manager.broadcast(response)
        try:
            while True:
                data = await websocket.receive_json()
                await manager.broadcast(data)
                print(data)
        except WebSocketDisconnect:
            manager.disconnect(websocket, sender)
            response['message'] = "left"
            await manager.broadcast(response)
