import re
import json
import bcrypt
import os

from flask import Blueprint, render_template, redirect, request, session, url_for, jsonify

import google_auth_oauthlib.flow
import googleapiclient.discovery

from ..utils import *
from ..models import *

bp = Blueprint('services_bp', __name__)

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/gmail.readonly'
          ]


@bp.route('/resetdb', methods=['POST'])
@admin_required
def service_resetdb():
    resetdb()

    return 'OK'


@bp.route('/register', methods=['POST'])
def service_register():
    data = request.get_data()
    try:
        data = json.loads(data)
        username = data['username']
        password = data['password']
        invitation_code = data['invitationCode']
    except:
        return '格式错误', 400

    if invitation_code != g.invitation_code:
        return '邀请码不正确', 403

    if not re.fullmatch(r'\w+', username):
        return '用户名仅含字母数字下划线', 400
    if not (2 <= len(username) <= 16):
        return '用户名的长度范围 [2, 16]', 400
    if not (8 <= len(password) <= 32):
        return '密码的长度范围 [8, 32]', 400
    if User.select().where(User.username == username):
        return '用户名已被使用', 422

    User.create(username=username, password_hash=bcrypt.hashpw(str.encode(password), bcrypt.gensalt()))

    return 'OK'


@bp.route('/login', methods=['POST'])
def services_login():
    data = request.get_data()
    try:
        data = json.loads(data)
        username = data['username']
        password = data['password']
    except:
        return '格式错误', 400

    try:
        user = User.get(User.username == username)
        assert bcrypt.checkpw(str.encode(password), str.encode(user.password_hash))
    except:
        return '用户名或密码错误', 401

    session['user_id'] = user.id
    session.permanent = True

    return 'OK'


@bp.route('/logout', methods=['POST'])
@login_required
def service_logout():
    session.pop('user_id')

    return 'OK'


@bp.route('/authorize', methods=['GET'])
def google_authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        os.getenv('CLIENT_SECRETS_FILE'), scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = url_for('services_bp.oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state

    return redirect(authorization_url)


@bp.route('/oauth2callback', methods=['GET'])
async def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        os.getenv('CLIENT_SECRETS_FILE'), scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('services_bp.oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    user_info = await get_user_info(credentials)

    credentials_dict = credentials_to_dict(credentials)
    # print(user_info)
    # print(credentials_dict)
    #
    try:
        # Check if user exists
        user = User.get(User.username == user_info['email'])
    except:
        # Create a new user
        user = User.create(username=user_info['email'],
                           password_hash=bcrypt.hashpw(str.encode('123456'), bcrypt.gensalt()),
                           google_cridential=credentials_dict)
    else:
        # Update user's google_cridential
        user.updateGoogleCridential(new_google_cridential=credentials_dict)

    session['user_id'] = user.id
    session.permanent = True

    return redirect(url_for('misc_bp.index'))


async def get_user_info(credentials):
    """Send a request to the UserInfo API to retrieve the user's information.

    Args:
    credentials: oauth2client.client.OAuth2Credentials instance to authorize the
                 request.
    Returns:
    User information as a dict.
    """
    user_info_service = googleapiclient.discovery.build(
        'oauth2', 'v2', credentials=credentials)

    return user_info_service.userinfo().get().execute()


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}
