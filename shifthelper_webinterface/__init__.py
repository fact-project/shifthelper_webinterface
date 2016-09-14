import os
from datetime import datetime, timedelta
import json

from flask import Flask, jsonify, render_template, redirect, request
from flask_login import login_user, login_required, logout_user
from flask_ldap3_login.forms import LDAPLoginForm
from flask_socketio import SocketIO
from flask_login import current_user

from twilio.rest import TwilioRestClient
from telepot import Bot
import peewee

from .authentication import login_manager, ldap_manager, basic_auth
from .communication import create_mysql_engine, place_call, send_message
from .database import Alert, database

with open(os.environ.get('SHIFTHELPER_CONFIG', 'config.json')) as f:
    config = json.load(f)

app = Flask(__name__)
app.secret_key = config['app']['secret_key']
app.config['user'] = config['app']['user']
app.config['password'] = config['app']['password']
app.users_awake = {}

login_manager.init_app(app)
ldap_manager.init_app(app)
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
    form = LDAPLoginForm()

    if form.validate_on_submit():
        login_user(form.user)
        return redirect('/')

    return render_template('index.html', form=form)


@app.route('/alerts', methods=['GET'])
def get_alerts():
    alerts = retrieve_alerts()
    return jsonify(alerts)


@app.route('/alerts', methods=['POST'])
@basic_auth.login_required
def post_alert():
    alert = request.args.to_dict()
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
        alert = Alert.select().where(Alert.uuid == uuid)
        return jsonify(alert.to_dict())
    except Alert.DoesNotExist:
        return jsonify(status='No such alert'), 404


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/')


@app.route('/testCall')
@login_required
def test_call():
    place_call(twillio_client, from_=config['twilio']['number'], database=fact_database)
    return render_template('call_placed.html')


@app.route('/testTelegram')
@login_required
def test_telegram():
    send_message(telegram_bot, database=fact_database)
    return render_template('message_sent.html')


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
