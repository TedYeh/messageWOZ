from typing import Optional, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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


class Dialog(BaseModel):
    dialogue_id: str
    services: List[str]
    turns: List[Turn]


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
async def create_dialog(dialog: Dialog):
    return dialog
