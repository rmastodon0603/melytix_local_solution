from flask_oauth import OAuth
from flask import request
from urllib.parse import parse_qsl

from user import User

FACEBOOK_APP_ID = '217283073022581'
FACEBOOK_APP_SECRET = 'b85df256a9c94ed3dbf1b8b2069de149'

oauth = OAuth()

facebook = oauth.remote_app('facebook',
                            base_url='https://graph.facebook.com/',
                            request_token_url=None,
                            access_token_url='/oauth/access_token',
                            authorize_url='https://www.facebook.com/dialog/oauth',
                            consumer_key=FACEBOOK_APP_ID,
                            consumer_secret=FACEBOOK_APP_SECRET,
                            request_token_params={'scope': 'ads_read'}
                            )


def prepare_fb_auth_redirect():
    return facebook.authorize(callback='https://127.0.0.1:5000/Facebook-login/callback')


def insert_fb_token_with_resp(email, resp):
    tokken = resp['access_token']
    User.insert_fb_token(email, tokken)


def fb_token_refresher(token):
    base_url = 'https://graph.facebook.com/oauth/access_token'
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': FACEBOOK_APP_ID,
        'client_secret': FACEBOOK_APP_SECRET,
        'fb_exchange_token': token
    }
    r = request.get(base_url, params=params)

    if r.status == 200:
        return dict(parse_qsl(r.text))
    else:
        return r.json()
