import os

# Third-party libraries
from flask import Flask, session, redirect, request, url_for, render_template

from bson.objectid import ObjectId

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user
)

import Google_auth
import GoogleAnalytics
import SearchConsole
# import Facebook_auth
import Utils
import YouTube

from user import User

app = Flask(__name__)
app.secret_key = os.urandom(24)

# User session management setup
login_manager = LoginManager()
login_manager.init_app(app)


# Flask-Login helper to retrieve a user from the db
@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    return User.get_by_id(ObjectId(user_id))


login_manager.login_view = 'login'


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return '<a class="button" href="/login" target="_top">Login</a>'
    else:
        try:
            print(YouTube.get_dash_yt_metrics(
                session['start_date'],
                session['end_date'])
            )
        except KeyError:
            return render_template('calendar.html')

        return render_template('home.html', id=current_user.id,
                               email=current_user.email, data=data,
                               sites=sites)


@app.route('/profile')
@login_required
def profile():
    return '<a href="/add_a_system">Connect google to Melytix</a>'


@app.route('/add_a_system', methods=['GET', 'POST'])
def systems():
    """POST user input from check boxes on connect_sys.html"""
    if request.method == 'POST':
        checked_boxes = request.form.getlist('Box')
        SCOPE = Utils.checkedboxed_to_scope(checked_boxes)
        User.add_scopes(current_user.email, SCOPE)
        Google_auth.Auth.SCOPE = SCOPE
        return redirect(url_for('google_login'))
    else:
        return render_template('connect_sys.html')


@app.route('/GA-Response', methods=['GET', 'POST'])
@login_required
def ga_response():
    account = request.form.get('acc_select')
    webProperty = request.form.get('prop_select')
    site = request.form.get('site_select')
    session['site'] = site
    session['viewid'] = GoogleAnalytics.g_get_viewid(account, webProperty)
    return render_template('calendar.html')


@app.route('/Dashboard')
@login_required
def dashboard():
    start_date = session['start_date']
    end_date = session['end_date']
    ga_data = GoogleAnalytics.google_analytics_query(session['viewid'],
                                                     start_date, end_date)

    sc_data = SearchConsole.make_sc_request(session['site'],
                                            start_date, end_date)

    metrics = Utils.prep_dash_metrics(ga_data, sc_data)

    return render_template('DashBoard.html', metrics=metrics)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = User.verify_password(email, password)
        if verify != 404 and verify:  # found an user and passwords match
            user = User.get_by_email(email)
            login_user(user, remember=True)
            return redirect(url_for('profile'))
        elif not verify:  # passwords does not match
            return render_template('Login.html', error='Email or password'
                                   'is incorrect')
        else:  # verify_password didn't find an user, 404
            return render_template('Login.html', error='Account with this'
                                   'email does not exist')
    else:
        return render_template('Login.html')


@app.route('/registration', methods=["POST"])
def registration():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if confirm_password == password:
            if User.get_by_email(email) is None:
                User.register(email, password)
                user = User.get_by_email(email)
                login_user(user)
                return redirect(url_for('profile'))
            else:
                return render_template("registration.html", error='Account'
                                       'already exists.')
        else:
            return render_template("registration.html",
                                   error='Wrong password confirmation.')
    else:
        return render_template("registration.html")


# @app.route('/Facebook-login')
# def facebook_login():
#     # Preparing Facebook redirect
#     return Facebook_auth.prepare_fb_auth_redirect()


# @app.route('/Facebook-login/callback')
# @Facebook_auth.facebook.authorized_handler
# def facebook_authorized(resp):
#     if resp is None:
#         return 'Access denied: reason={} error={}'.format(
#             request.args['error_reason'],
#             request.args['error_description']
#         )
#     print("resp = ", resp)
#     Facebook_auth.insert_fb_token_with_resp(current_user.email, resp)
#     return redirect(url_for('index'))


@app.route('/Google-login')
@login_required
def google_login():
    # Preparing google auth redirect
    print(Google_auth.Auth.SCOPE)
    return redirect(Google_auth.prepare_google_auth_redirect())


# User Google login Functionality
@app.route('/login/callback')
@login_required
def callback():
    data = Google_auth.request_data_from_google(request.args)
    resp = data['resp']
    token = data['token']
    if resp.status_code == 200:
        # Code 200 - Request is successful
        user_data = resp.json()
        # add the tokens to user db
        Google_auth.add_tokens_to_user(current_user.email, user_data, token)

        # Send user back to homepage
        return redirect(url_for("index"))
    # Request is not successful
    return 'Could not fetch your information.'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/run', methods=['POST'])
@login_required
def run():
    if request.method == 'POST':
        dates = request.get_json()
        session['start_date'] = dates.get('dateFrom')[0:10]
        session['end_date'] = dates.get('dateTo')[0:10]
        return redirect(url_for('run_done'))


@app.route('/run/done')
@login_required
def run_done():
    """Some work around ajax
       TODO: Needs fixing """
    print('done')
    return redirect(None)


if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True, ssl_context="adhoc")
