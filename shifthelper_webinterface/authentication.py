from flask_ldap3_login import LDAP3LoginManager
from flask_login import LoginManager, UserMixin
from flask import redirect

users = {}

config = {
    'LDAP_HOST': 'fact-project.org',
    'LDAP_BASE_DN': 'dc=fact,dc=iac,dc=es',
    'LDAP_USER_DN': 'ou=People',
    'LDAP_USER_RDN_ATTR': 'cn',
    'LDAP_USER_LOGIN_ATTR': 'uid',
    'LDAP_BIND_USER_DN': None,
    'LDAP_BIND_USER_PASSWORD': None,
}

ldap_manager = LDAP3LoginManager()
ldap_manager.init_config(config)
login_manager = LoginManager()


class User(UserMixin):
    def __init__(self, dn, username, data):
        self.dn = dn
        self.username = username
        self.data = data

    def __repr__(self):
        return self.dn

    def get_id(self):
        return self.dn


@login_manager.user_loader
def load_user(id_):
    return users.get(id_, None)


@ldap_manager.save_user
def save_user(dn, username, data, memberships):
    user = User(dn, username, data)
    users[dn] = user
    return user
