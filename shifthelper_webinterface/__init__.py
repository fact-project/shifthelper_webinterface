import os
from datetime import datetime, timedelta
import json

from flask import Flask, jsonify, render_template, redirect, request, flash, Markup, Response
from flask_login import login_user, login_required, logout_user
from flask_socketio import SocketIO
from flask_login import current_user

from twilio.rest import TwilioRestClient
from twilio.exceptions import TwilioException
from telepot import Bot
from telepot.exception import TelegramError
from time import sleep
import peewee
import eventlet

import subprocess as sp

from .authentication import login_manager, basic_auth, authenticate_user
from .communication import create_mysql_engine, place_call, send_message
from .database import Alert, database


eventlet.monkey_patch()


with open(os.environ.get('SHIFTHELPER_CONFIG', 'config.json')) as f:
    config = json.load(f)

app = Flask(__name__)
app.secret_key = config['app']['secret_key']
app.config['user'] = config['app']['user']
app.config['password'] = config['app']['password']
app.users_awake = {}
app.dummy_alerts = {}
app.config['shifthelper_log'] = config['app']['shifthelper_log']

login_manager.init_app(app)
socket = SocketIO(app)

twillio_client = TwilioRestClient(**config['twilio']['client'])
fact_database = create_mysql_engine(**config['fact_database'])
telegram_bot = Bot(config['telegram']['bot_token'])

database.init(**config['database'])


@app.before_first_request
def init_db():
    database.connect()
    database.create_tables([Alert], safe=True)
    database.close()


@app.before_request
def _db_connect():
    database.connect()


@app.teardown_request
def _db_close(exc):
    if not database.is_closed():
        database.close()


def remove_alert(uuid):
    (
        Alert.select()
        .where(Alert.uuid == uuid)
        .get()
    ).delete_instance()


def add_alert(alert):
    alert['acknowledged'] = False
    Alert(**alert).save()


def acknowledge_alert(uuid):
    alert = (
        Alert.select()
        .where(Alert.uuid == uuid)
        .get()
    )
    alert.acknowledged = True
    alert.save()


def retrieve_alerts():
    comp_date = datetime.utcnow() - timedelta(hours=24)
    alerts = (
        Alert
        .select()
        .order_by(Alert.timestamp.desc())
        .where(Alert.timestamp > comp_date)
    )
    return [alert.to_dict() for alert in alerts]


def update_clients():
    alerts = retrieve_alerts()
    socket.emit('update', json.dumps(alerts))


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')


@app.route('/log')
@login_required
def log():
    return render_template('log.html')


@app.route('/logstrem')
@login_required
def logstream():
    def generate():
        first = True
        with open(app.config['shifthelper_log']) as f:
            while True:
                text = f.read()
                if first:
                    yield '\n'.join(text.splitlines()[-100:])
                    first = False
                yield text
                sleep(1)

    return Response(generate())


@app.route('/alerts', methods=['GET'])
def get_alerts():
    alerts = retrieve_alerts()
    return jsonify(alerts)


@app.route('/alerts', methods=['POST'])
@basic_auth.login_required
def post_alert():
    alert = request.json
    try:
        add_alert(alert)
    except peewee.InternalError as e:
        return jsonify(status='Could not add alert', message=str(e)), 422

    update_clients()
    return jsonify(status='ok')


@app.route('/alerts/<uuid>', methods=['PUT', 'DELETE'])
@login_required
def update_alert(uuid):

    if request.method == 'PUT':
        try:
            acknowledge_alert(uuid)
            update_clients()
            return jsonify(status='ok')
        except Alert.DoesNotExist:
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
        alert = Alert.get(uuid=uuid)
        return jsonify(alert.to_dict())
    except Alert.DoesNotExist:
        return jsonify(status='No such alert'), 404


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return redirect('/')

    username = request.form['username']
    password = request.form['password']

    user = authenticate_user(username, password)

    if user is not None:
        login_user(user)
        return redirect('/')
    else:
        flash('Wrong username/password', 'alert-danger')
        return redirect('/')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/')


@app.route('/testCall')
@login_required
def test_call():
    try:
        place_call(
            twillio_client,
            from_=config['twilio']['number'],
            database=fact_database
        )
        flash('I will call you now', 'alert-success')
        return redirect('/')
    except (ValueError, IndexError):
        flash(Markup(render_template('no_number.html')), 'alert-danger')
        return redirect('/')
    except TwilioException:
        flash(Markup(render_template('call_failed.html')), 'alert-danger')
        return redirect('/')


@app.route('/testTelegram')
@login_required
def test_telegram():
    try:
        send_message(telegram_bot, database=fact_database)
        flash('I send you a message', 'alert-success')
        return redirect('/')
    except (ValueError, IndexError):
        flash(Markup(render_template('telegram_failed.html')), 'alert-danger')
        return redirect('/')
    except TelegramError:
        flash(Markup(render_template('telegram_new_user.html')), 'alert-danger')
        return redirect('/')


@app.route('/iAmAwake', methods=['POST'])
@login_required
def i_am_awake():
    app.users_awake[current_user.username] = datetime.utcnow()
    return redirect('/')


@app.route('/iAmAwake', methods=['GET'])
def who_is_awake():
    users_awake = dict(zip(
        app.users_awake.keys(),
        map(str, app.users_awake.values())
    ))
    return jsonify(users_awake)



@app.route('/dummyAlert', methods=['POST'])
@login_required
def post_dummy_alert():
    app.dummy_alerts[current_user.username] = datetime.utcnow()
    return redirect('/')


@app.route('/dummyAlert', methods=['GET'])
def get_dummy_alert():
    dummy_alerts = dict(zip(
        app.dummy_alerts.keys(),
        map(str, app.dummy_alerts.values())
    ))
    return jsonify(dummy_alerts)
