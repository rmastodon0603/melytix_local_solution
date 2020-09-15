from flask_login import UserMixin
import pymongo
import os
from hashlib import pbkdf2_hmac

# Connecting to Mogodb Atlas
collection = pymongo.MongoClient(
    'mongodb+srv://MaxTeslya:7887334Mna@melytixdata'
    '-ryedw.mongodb.net/test?retryWrites=true&w=majority')

db = collection.MelytixUsers.Users


class User(UserMixin):
    def __init__(self, id_, email, password):
        self.id = id_
        self.email = email
        self.password = password
        # self.google_access_token = google_access_token
        # self.google_refresh_token = google_refresh_token
        # self.fb_access_token = fb_access_token

    @staticmethod
    def get_by_email(email: str):
        user = db.find_one({'email': email})
        if user:
            log_user = User(id_=str(user['_id']), email=user['email'],
                            password=user['password'])

            try:
                log_user.google_access_token = user['g_access_token']
                log_user.google_refresh_token = user['g_refresh_token']
            except KeyError:
                pass

            try:
                log_user.metrics = user['metrics']
            except KeyError:
                pass
            return log_user
        else:
            return None

    @staticmethod
    def get_by_id(user_id):
        user = db.find_one({'_id': user_id})
        if user:
            log_user = User(id_=str(user['_id']), email=user['email'],
                            password=user['password'])

            try:
                log_user.google_access_token = user['tokens']['g_access_token']
                log_user.google_refresh_token = user['tokens']['g_refresh_token']
            except KeyError:
                pass

            try:
                log_user.metrics = user['metrics']
            except KeyError:
                pass
            return log_user
        else:
            return None
        return log_user

    @staticmethod
    def register(email: str, passwrd: str) -> None:
        salt = os.urandom(24)
        passwrd = pbkdf2_hmac('sha256', passwrd.encode('utf-8'), salt, 100000)
        db.insert_one({
            'email': email,
            'password': passwrd,
            'salt': salt
        })

    @staticmethod
    def verify_password(email, inputted_pass):
        user = db.find_one({'email': email})
        if user:
            salt = user['salt']
            inputted_pass = pbkdf2_hmac(
                'sha256',
                inputted_pass.encode('utf-8'),
                salt,
                100000)
            if user['password'] == inputted_pass:
                return True
            else:
                return False
        else:
            return 404

    @staticmethod
    def add_scopes(email: str, scope: list):
        """adding scopes for google apis in the database for future usage

        Args:
            email (str): the email that we use to find the user
            scope (list): the scopes that we are adding
        """
        db.find_one_and_update(
            {'email': email},
            {'$set': {
                'SCOPE': scope
            }},
            upsert=False
        )

    @staticmethod
    def insert_tokens(email: str, access_token: str, refresh_token: str):
        """Mongodb find adn update func for adding user tokens in db

        Args:
            email: the email that we use to find the user
            access_token: the google access token
            refresh_token: the google refresh token"""
        db.find_one_and_update(
            {'email': email},
            {'$set': {
                'tokens': {'g_access_token': access_token,
                           'g_refresh_token': refresh_token}
            }},
            upsert=False
        )

    """@staticmethod
    def get_by_email(email):
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE email = ?", (email,)
        ).fetchone()

        if not user:
            return None
        user = User(
            id_=user[0], email=user[1],
            password=user[2], google_access_token=user[3],
            google_refresh_token=user[4], fb_access_token=user[5])
        return user

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE id = ?", user_id
        ).fetchone()

        if not user:
            return None
        user = User(
            id_=user[0], email=user[1],
            password=user[2], google_access_token=user[3],
            google_refresh_token=user[4], fb_access_token=user[5]
        )
        return user

    @staticmethod
    def create(email, password, google_access_token,
               google_refresh_token, fb_access_token):
        db = get_db()
        db.execute(
            "INSERT INTO user (email, password, google_access_token,"
            "google_refresh_token, fb_access_token) "
            "VALUES (?, ?, ?, ?, ?)",
            (email, password, google_access_token,
             google_refresh_token, fb_access_token),
        )
        db.commit()

    @staticmethod
    def get_google_token(user_id):
        db = get_db()
        token = db.execute(
            "SELECT google_access_token FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        if not token:
            return None

        return token

    @staticmethod
    def get_google_refresh_token(user_id):
        db = get_db()
        refresh_token = db.execute(
            "SELECT google_refresh_token FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        if not refresh_token:
            return None
        return refresh_token

    @staticmethod
    def insert_tokens(email, g_access_token, g_refresh_token):
        db = get_db()
        db.execute(
            "UPDATE user SET google_access_token = ?,"
            "google_refresh_token = ? WHERE email = ?",
            (g_access_token, g_refresh_token, email)
        )
        db.commit()

    @staticmethod
    def get_fb_token(user_id):
        db = get_db()
        token = db.execute(
            "SELECT fb_access_token FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        if not token:
            return None
        return token

    @staticmethod
    def insert_fb_token(email, fb_access_token):
        db = get_db()
        db.execute(
            "UPDATE user SET fb_access_token = ? WHERE email = ?",
            (fb_access_token, email)
        )
        db.commit()

    @staticmethod
    def create_ga_table(user_id, data):
        sessions = data['sessions']
        users = data['users']
        pageviews = data['pageviews']
        pageviewsPerSession = data['pageviewsPerSession']
        avgSessionDuration = data['avgSessionDuration']
        bounces = data['bounces']
        percentNewSession = data['percentNewSession']
        NewVisitors = data['NewVisitors']
        ReturningVisitors = data['ReturningVisitors']
        ga_db = get_ga_db()
        ga_db.execute(
            "INSERT INTO ga_data (id ,sessions, users, pageviews,"
            "pageviewsPerSession, avgSessionDuration, bounces, "
            "percentNewSession, NewVisitors, ReturningVisitors) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, sessions, users, pageviews,
             pageviewsPerSession, avgSessionDuration,
             bounces, percentNewSession, NewVisitors, ReturningVisitors)
        )
        ga_db.commit()

    @staticmethod
    def get_ga_data(user_id):
        ga_db = get_ga_db()
        data = ga_db.execute(
            "SELECT * FROM ga_data WHERE id = ?", (user_id,)
        ).fetchone()

        if not data:
            return None
        ga_data = {
            'sessions': data[1],
            'users': data[2],
            'pageviews': data[3],
            'pageviewsPerSession': data[4],
            'avgSessionDuration': data[5],
            'bounces': data[6],
            'percentNewSession': data[7],
            'NewVisitors': data[8],
            'ReturningVisitors': data[9]
        }
        return ga_data

    @staticmethod
    def update_ga_data(user_id, data):
        sessions = data['sessions']
        users = data['users']
        pageviews = data['pageviews']
        pageviewsPerSession = data['pageviewsPerSession']
        avgSessionDuration = data['avgSessionDuration']
        bounces = data['bounces']
        percentNewSession = data['percentNewSession']
        NewVisitors = data['NewVisitors']
        ReturningVisitors = data['ReturningVisitors']
        ga_db = get_ga_db()
        ga_db.execute(
            "UPDATE ga_data SET sessions = ?, users = ?,"
            "pageviews = ?, pageviewsPerSession = ?,"
            "avgSessionDuration = ""?, bounces = ?,"
            "percentNewSession = ?, NewVisitors = ?,"
            "ReturningVisitors = ? WHERE id = ?",
            (sessions, users, pageviews,
             pageviewsPerSession, avgSessionDuration,
             bounces, percentNewSession, NewVisitors,
             ReturningVisitors, user_id)
        )
        ga_db.commit()
"""
