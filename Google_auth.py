from flask import session, redirect, url_for, request
from flask_login import current_user

from user import User
from flask_login import login_user

from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
from oauth2client import client as oauth_client
import httplib2 as lib2
from datetime import datetime, timedelta


class Auth:
    CLIENT_ID = '991095477102-ri4l91vfqokh9m54adkvblvep5os62hv.apps.' \
                'googleusercontent.com'
    CLIENT_SECRET = 'gaybEvYyLOe13f8ZroRwv5DN'
    REDIRECT_URI = 'https://127.0.0.1:5000/login/callback'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = []  # will be filled on choose systems stage


def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            Auth.CLIENT_ID,
            state=state,
            redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth


def prepare_google_auth_redirect():
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, prompt='select_account', access_type='offline')
    session['oauth_state'] = state
    return auth_url


def request_data_from_google(callback):
    if 'error' in callback:
        if callback.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in callback and 'state' not in callback:
        return redirect(url_for('login'))
    else:
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        data = {'resp': resp, 'token': token}
        return data


def add_tokens_to_user(email, user_data, token):
    # Adding auth tokens into the db
    if user_data.get('verified_email'):
        user_access_token = token.get('access_token')
        user_refresh_token = token.get('refresh_token')
        User.insert_tokens(email, user_access_token, user_refresh_token)
        user = User.get_by_email(current_user.email)
        login_user(user)
    else:
        return "User email not available or not verified by Google.", 400


def auth_credentials():
    credentials = oauth_client.GoogleCredentials(
        access_token=current_user.google_access_token,
        refresh_token=current_user.google_refresh_token,
        client_id=Auth.CLIENT_ID,
        client_secret=Auth.CLIENT_SECRET,
        token_uri='https://accounts.google.com/o/oauth2/token',
        token_expiry=(datetime.now() + timedelta(days=10)),
        user_agent='Melytix-user-agent/1.0')
    # authorizing credentials (if token is expired it will refresh it)
    authorized = credentials.authorize(lib2.Http())
    return authorized
