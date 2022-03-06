from fastapi import (
    FastAPI, WebSocket, WebSocketDisconnect, Request, Response
)
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from schema import *
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
import json
import os
import uvicorn
import glob

app = FastAPI()

# -------------------websocket 多人連線對話部分-------------------
# locate templates
templates = Jinja2Templates(directory="templates")


@app.get("/") # 主頁(登入頁面)，選擇你要擔任的腳色(SYSTEM、USER)
def get_home(request: Request): 
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/chat") # 聊天頁面，目前已將原index.html做整合
def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/api/current_user") # 確認目前腳色是SYSTEM or USER
def get_user(request: Request):
    return request.cookies.get("X-Authorization")

@app.get("/schema") # 確認目前腳色是SYSTEM or USER
async def get_new_task():
    return schema_data.get_random_schema()

class RegisterValidator(BaseModel): # 接收使用者名稱用
    username: str

    class Config:
        orm_mode = True


@app.post("/api/register") # 在home.html使用而已，做腳色註冊用
def register_user(user: RegisterValidator, response: Response):
    response.set_cookie(key="X-Authorization", value=user.username, httponly=True)


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

