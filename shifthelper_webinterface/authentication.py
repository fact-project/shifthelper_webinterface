from flask_login import LoginManager, UserMixin
from flask import current_app
from flask_httpauth import HTTPBasicAuth

import requests

users = {}

login_manager = LoginManager()
basic_auth = HTTPBasicAuth()


class User(UserMixin):
    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return 'User(username={})'.format(self.username)

    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(id_):
    return users.get(id_, None)


def authenticate_user(username, password):
    ret = requests.post(
        'https://fact-project.org/auth/index.php',
        data={'username': username, 'password': password}
    )

    login_successful = ret.status_code == 200

    if login_successful is True:
        user = User(username)
        if username not in users:
            users[username] = user
        return user
    else:
        return None


@basic_auth.get_password
def get_pw(username):
    if username == current_app.config['user']:
        return current_app.config['password']
    else:
        return None
