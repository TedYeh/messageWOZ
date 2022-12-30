import re
import json
import bcrypt
import os
import base64
import bs4

from flask import Blueprint, render_template, redirect, request, session, url_for, jsonify

import google.oauth2.credentials
import googleapiclient.discovery
from email.mime.text import MIMEText

from ..utils import *
from ..models import *

bp = Blueprint('gmail_bp', __name__)


@bp.route('/gmail_db.json', methods=['GET'])
@login_required
def get_mails():
    """ Get mails from gmail account.

    Args:
      None

    Returns:
      json: json object with mails.
    """
    max_results = 50

    # Get the user's google credentials from database
    credentials = get_credentials()

    # Get the user's email list from gmail API
    service = googleapiclient.discovery.build('gmail', 'v1', credentials=credentials)
    message_id_list = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
    message_list = []
    for message_id in message_id_list['messages']:
        message = service.users().messages().get(userId='me', id=message_id['id']).execute()
        message_format_data = message_to_format_data(message)
        message_list.append(message_format_data)
    return json.dumps(message_list, ensure_ascii=False, indent=4), 200, {'Content-Type': 'application/json'}


@bp.route('/id_list', methods=['GET'])
@login_required
def get_mail_id_list():
    """ Get mail id list from gmail account.

    Args:
      None

    Returns:
      json: json object with mail id.
    """
    max_results = 50

    # Get the user's google credentials from database
    credentials = get_credentials()

    # Get the user's email id list from gmail API
    service = googleapiclient.discovery.build('gmail', 'v1', credentials=credentials)
    message_id_list = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
    return json.dumps(message_id_list, ensure_ascii=False, indent=4), 200, {'Content-Type': 'application/json'}


@bp.route('/sent', methods=['POST'])
@login_required
def sent_mail():
    """ Send an email by gmail API

    Args:
      request_data: The message to be sent.

    Returns:
      A json object containing the message id.
    """
    credentials = get_credentials()
    service = googleapiclient.discovery.build('gmail', 'v1', credentials=credentials)
    request_data = request.get_json()
    mail = create_mail(request_data)
    try:
        result = service.users().messages().send(userId='me', body=mail).execute()
        return jsonify(result), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500, {'Content-Type': 'application/json'}


def create_mail(request_data):
    """ Createa message for an email.

    Args:
      request_data: The message to be created.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEText(request_data['信件內容'])

    if '郵件主旨' in request_data:
        message['Subject'] = request_data['郵件主旨']
    if '寄件者' in request_data:
        message['From'] = request_data['寄件者']
    if '收件者' in request_data:
        message['To'] = request_data['收件者']
    if '副本收件者' in request_data:
        message['Cc'] = request_data['副本收件者']
    if '密件副本收件者' in request_data:
        message['Bcc'] = request_data['密件副本收件者']

    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    return {'raw': raw}


def message_to_format_data(message):
    """ Convert message to format data.

    Args:
      message: The message to be converted.

    Returns:
      A dict containing the message's format data.
    """
    message_dict = {}

    for header in message['payload']['headers']:
        if str.lower(header['name']) == 'subject':
            message_dict['郵件主旨'] = header['value']
        elif str.lower(header['name']) == 'from':
            message_dict['寄件者'] = split_name_and_address(header['value'])
        elif str.lower(header['name']) == 'to':
            message_dict['收件者'] = split_name_and_address(header['value'])
        elif str.lower(header['name']) == 'cc':
            message_dict['副本收件者'] = split_name_and_address(header['value'])
        elif str.lower(header['name']) == 'bcc':
            message_dict['密件副本收件者'] = split_name_and_address(header['value'])
        elif str.lower(header['name']) == 'date':
            message_dict['日期'] = header['value']

    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/html' and 'data' in part['body']:
                # decode the base64 encoded message
                message_content_html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                # remove html tags by beautiful soup
                message_dict['內容'] = bs4.BeautifulSoup(message_content_html, 'html.parser').get_text()
            elif part['mimeType'] == 'text/plain' and 'data' in part['body']:
                # decode the base64 encoded message
                try:
                    message_dict['內容'] = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                except:
                    pass
    else:
        if 'text/html' in message['payload']['mimeType'] and 'data' in message['payload']['body']:
            # decode the base64 encoded message
            message_content_html = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
            # remove html tags by beautiful soup
            message_dict['內容'] = bs4.BeautifulSoup(message_content_html, 'html.parser').get_text()
        elif 'text/plain' in message['payload']['mimeType'] and 'data' in message['payload']['body']:
            # decode the base64 encoded message
            message_dict['內容'] = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')

    return [message_dict['郵件主旨'], message_dict]


def split_name_and_address(name_and_address):
    """ Split name and address.

    Args: name_and_address: The name and address to be split. (ex: '"NAME" <ADDRESS>' or 'ADDRESS'), if have multiple
    address, split by ','.

    Returns:
      A list containing the [NAME, ADDRESS], if the name_and_address only contains ADDRESS, return [None, ADDRESS]
    """
    def split_address_to_list(address):
        split_result = re.split('\'|"|<|>', address)
        split_result = [item.strip() for item in split_result]
        split_result = list(filter(lambda a: len(a) > 0, split_result))
        
        if len(split_result) == 1:
            if (bool(re.search('@', split_result[0]))):
                return ["", split_result[0]]
            else:
                return [split_result[0], ""]
        elif len(split_result) > 0:
            return [split_result[0], split_result[1]]
        else:
            return ["", ""]

    result = []
    name_and_address_list = name_and_address.split(',')
    for address in name_and_address_list:
        result.append(split_address_to_list(address))

    return result


def get_credentials():
    """ Gets valid user credentials from storage.

    Args:
      None

    Returns:
      The credentials object.
    """
    user_id = session['user_id']
    user = User.get(User.id == user_id)
    cred = google.oauth2.credentials.Credentials(token=user.google_cridential['token'],
                                                 refresh_token=user.google_cridential['refresh_token'],
                                                 client_id=user.google_cridential['client_id'],
                                                 client_secret=user.google_cridential['client_secret'],
                                                 token_uri=user.google_cridential['token_uri'],
                                                 scopes=user.google_cridential['scopes'])
    return cred

