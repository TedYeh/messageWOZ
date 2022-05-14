import os
from datetime import timedelta
from flask_socketio import SocketIO, emit
import flask_socketio

from data_labelling.redis import rd
from .app import app
from .admin import admin
from .models import *
from . import routes


def run():
    running_rooms = Room.select().where(Room.status_code == Room.Status.RUNNING.value)
    for room in running_rooms:
        room.task.finished = False
        room.task.save()
        room.status = Room.Status.ABORTED
        room.save()

    admin.init_app(app)
    rd.flushall()

    socket_io = SocketIO(app, cors_allowed_origins="*")
    socket_io.init_app(app, cors_allowed_origins="*")
    socket_io.run(app, host='0.0.0.0', port=5000, keyfile='server.key', certfile='server.crt')
