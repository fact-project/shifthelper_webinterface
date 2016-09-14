import os
import datetime
import json
import logging

from flask import Flask, jsonify, render_template, redirect, request
from flask_login import login_user, login_required, logout_user
from flask_ldap3_login.forms import LDAPLoginForm
from flask_socketio import SocketIO
from flask_login import current_user

from twilio.rest import TwilioRestClient
from telepot import Bot

from .authentication import login_manager, ldap_manager, basic_auth
from .communication import create_mysql_engine, place_call, send_message

with open(os.environ.get('SHIFTHELPER_CONFIG', 'config.json')) as f:
    config = json.load(f)

app = Flask(__name__)
app.secret_key = config['app']['secret_key']
app.config['user'] = config['app']['user']
app.config['password'] = config['app']['password']
app.alerts = {}
app.users_awake = {}

login_manager.init_app(app)
ldap_manager.init_app(app)
socket = SocketIO(app)

twillio_client = TwilioRestClient(**config['twilio']['client'])
database = create_mysql_engine(**config['database'])
telegram_bot = Bot(config['telegram']['bot_token'])


def remove_alert(uuid):
    app.alerts.pop(uuid)


def update_clients():
    alerts = list(app.alerts.values())
    alerts.sort(key=lambda m: m['timestamp'], reverse=True)
    socket.emit('update', json.dumps(alerts))


@app.route('/', methods=["GET", "POST"])
def index():
    form = LDAPLoginForm()

    if form.validate_on_submit():
        login_user(form.user)
        return redirect('/')

    return render_template('index.html', form=form)


@app.route('/alerts', methods=['GET'])
def get_alerts():
    return jsonify(list(app.alerts.values()))


@app.route('/alerts', methods=['POST'])
@basic_auth.login_required
def post_alert():
    alert = request.args.to_dict()

    try:
        level = logging.getLevelName(int(alert['level']))
    except:
        level = alert['level']

    alert['level'] = level
    alert['acknowledged'] = False

    key = alert['uuid']
    app.alerts[key] = alert

    update_clients()

    return jsonify(status='ok')


@app.route('/alerts/<uuid>', methods=['PUT', 'DELETE'])
@login_required
def update_alert(uuid):

    if request.method == 'PUT':
        try:
            app.alerts[uuid]['acknowledged'] = True
            update_clients()
            return jsonify(status='ok')
        except KeyError:
            return jsonify(status='No such alert'), 404

    elif request.method == 'DELETE':
        try:
            uuid = request.args['uuid']
            remove_alert(uuid)
            update_clients()
        except KeyError:
            return jsonify(status='No such alert'), 404


@app.route('/alerts/<uuid>', methods=['GET'])
def get_alert(uuid):
    try:
        return jsonify(app.alerts[uuid])
    except KeyError:
        return jsonify(status='No such alert'), 404


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/')


@app.route('/testCall')
@login_required
def test_call():
    place_call(twillio_client, from_=config['twilio']['number'], database=database)
    return render_template('call_placed.html')


@app.route('/testTelegram')
@login_required
def test_telegram():
    send_message(telegram_bot, database=database)
    return render_template('message_sent.html')


@app.route('/iAmAwake', methods=['POST'])
@login_required
def i_am_awake():
    app.users_awake[current_user.username] = datetime.datetime.utcnow()
    return redirect('/')


@app.route('/iAmAwake', methods=['GET'])
def who_is_awake():
    return jsonify(app.users_awake)
