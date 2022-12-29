import string
import random

from flask import Flask, session, g

from .models import *
from .routes import *

import os
from datetime import timedelta
from flask_socketio import SocketIO, emit
import flask_socketio

from .redis import rd
from .admin import admin
from .models import *
from . import routes


app = Flask(__name__)

app.register_blueprint(misc.bp, url_prefix='')
app.register_blueprint(room.bp, url_prefix='/room')
app.register_blueprint(services.bp, url_prefix='/services')
app.register_blueprint(match.bp, url_prefix='/match')
app.register_blueprint(gmail.bp, url_prefix='/gmail')
app.register_blueprint(gcalendar.bp, url_prefix='/gcalendar')

app.config.from_pyfile('settings.py')

running_rooms = Room.select().where(Room.status_code == Room.Status.RUNNING.value)
for room in running_rooms:
    room.task.finished = False
    room.task.save()
    room.status = Room.Status.ABORTED
    room.save()

admin.init_app(app)
rd.flushall()

socket_io = SocketIO(app, cors_allowed_origins="*")
# socket_io.init_app(app, cors_allowed_origins="*")
# socket_io.run(app, host='0.0.0.0', port=5000, keyfile='server.key', certfile='server.crt')

invitation_code = '959592'

@app.before_request
def before_request():
    g.invitation_code = invitation_code

    user_id = session.get('user_id')
    try:
        g.me = User.get(User.id == user_id)
    except:
        g.me = None
