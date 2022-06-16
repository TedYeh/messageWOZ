import re
import json
import bcrypt
import os
import datetime

from flask import Blueprint, render_template, redirect, request, session, url_for, jsonify

import google.oauth2.credentials
from googleapiclient.discovery import build

from ..utils import *
from ..models import *

bp = Blueprint('gcalendar_bp', __name__)


@bp.route('/gcalendar_db.json', methods=['GET'])
@login_required
def get_events():
    """ Get the events from google calendar

    Args:
        None

    Returns:
        events: a list of events
    """
    max_results = 50
    q = None

    # Get the user's events from the google calendar
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    service = build('calendar', 'v3', credentials=get_credentials())
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=max_results, singleEvents=True,
                                          orderBy='startTime', q=q).execute()
    events = events_result.get('items', [])
    calendar_db = events_to_format_list(events)

    if not events:
        return json.dumps([]), 200, {'Content-Type': 'application/json'}
    else:
        return json.dumps(calendar_db, ensure_ascii=False, indent=4), 200, {'Content-Type': 'application/json'}


@bp.route('/create', methods=['POST'])
@login_required
def create_event():
    """ Create an event in google calendar

    Args:
        None

    Returns:
        Result: a json of the result
    """
    event = request.get_json()
    service = build('calendar', 'v3', credentials=get_credentials())
    event = service.events().insert(calendarId='primary', body=event).execute()
    return jsonify(event), 200, {'Content-Type': 'application/json'}


def events_to_format_list(events):
    """ Convert the events to a format that can be used by the frontend

    Args:
        events: a list of events

    Returns:
        calendar_db: a list of dictionaries
    """
    events_list = []
    for item in events:
        e = dict()
        e['領域'] = 'Calendar'
        e['活動名稱'] = item['summary']
        e['參加者'] = [attendee['email'] for attendee in item['attendees']] if 'attendees' in item else []
        e['活動內容'] = item['description'] if 'description' in item else ''
        e['活動地點'] = item['location'] if 'location' in item else ''
        if 'date' in item['start']:
            e['是否全天'] = '是'
            e['活動時間'] = [item['start']['date'], item['end']['date']]
        else:
            e['是否全天'] = '否'
            e['活動時間'] = [item['start']['dateTime'], item['end']['dateTime']]
        events_list.append([e['活動名稱'], e])
    return events_list


def get_credentials():
    """ Gets valid user credentials from storage.

    Args:
        None

    Returns:
      The credentials object.
    """
    # Get the user's google credentials from database
    user_id = session['user_id']
    user = User.get(User.id == user_id)
    cred = google.oauth2.credentials.Credentials(token=user.google_cridential['token'],
                                                 refresh_token=user.google_cridential['refresh_token'],
                                                 client_id=user.google_cridential['client_id'],
                                                 client_secret=user.google_cridential['client_secret'],
                                                 token_uri=user.google_cridential['token_uri'],
                                                 scopes=user.google_cridential['scopes'])
    return cred
