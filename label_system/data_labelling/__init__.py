import os
from datetime import timedelta
from flask_socketio import SocketIO, emit
import flask_socketio


from data_labelling.redis import rd
from .admin import admin
from .models import *
from . import routes

# TODO
if os.path.isfile('app.db'):
    from .app import app