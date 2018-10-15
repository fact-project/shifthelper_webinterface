import os
from datetime import datetime, timedelta
import json

import eventlet
eventlet.monkey_patch()

from flask import (
    Flask, jsonify, render_template, redirect,
    request, flash, Markup, Response, stream_with_context,
)
from flask_login import login_user, login_required, logout_user
from flask_socketio import SocketIO
from flask_login import current_user

from twilio.rest import TwilioRestClient
from twilio.exceptions import TwilioException
from telepot import Bot
from telepot.exception import TelegramError
import peewee

from .authentication import login_manager, basic_auth, authenticate_user
from .communication import create_mysql_engine, place_call, send_message
from .database import Alert, database_proxy
from .log import log_generator


with open(os.environ.get('SHIFTHELPER_CONFIG', 'config.json')) as f:
    config = json.load(f)

app = Flask(__name__)
app.secret_key = config['app'].pop('secret_key')
app.config.update(config['app'])
app.users_awake = {}
app.dummy_alerts = {}
app.heartbeats = {
    # on startup we pretend, to have got a single heartbeat already.
    'shifthelperHeartbeat': datetime.utcnow() - timedelta(minutes=9),
    'heartbeatMonitor': datetime.utcnow() - timedelta(minutes=9),
}

login_manager.init_app(app)
socket = SocketIO(app)

twillio_client = TwilioRestClient(**config['twilio']['client'])
fact_database = create_mysql_engine(**config['fact_database'])
telegram_bot = Bot(config['telegram']['bot_token'])

if app.config['DEBUG']:
    database = peewee.SqliteDatabase('webinterface.sqlite')
else:
    database = peewee.MySQLDatabase(**config['database'])

database_proxy.initialize(database)


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
    Alert.delete().where(Alert.uuid == uuid).execute()


def add_alert(alert):
    alert['acknowledged'] = False
    Alert.insert(**alert).execute()


def acknowledge_alert(uuid):
    Alert.update(acknowledged=True).where(Alert.uuid == uuid).execute()


def retrieve_alerts():
    comp_date = datetime.utcnow() - timedelta(hours=24)
    alerts = (
        Alert
        .select()
        .order_by(Alert.timestamp.desc())
        .where(Alert.timestamp > comp_date)
    )
    return [alert.to_dict() for alert in alerts]


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')


@app.route('/log')
@login_required
def log():
    return render_template('log.html')


@app.route('/logstream')
@login_required
def logstream():
    return Response(
        stream_with_context(log_generator()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache'}
    )


@app.route('/alerts', methods=['GET'])
def get_alerts():
    alerts = retrieve_alerts()
    return jsonify(alerts)


@app.route('/alerts', methods=['POST'])
@basic_auth.login_required
def post_alert():
    alert = request.json
    if not alert:
        return jsonify(status="Received empty json object"), 400
    try:
        add_alert(alert)
    except peewee.InternalError as e:
        return jsonify(status='Could not add alert', message=str(e)), 422

    socket.emit('updateAlerts')
    return jsonify(status='ok')


@app.route('/alerts/<uuid>', methods=['PUT', 'DELETE'])
@login_required
def update_alert(uuid):

    if request.method == 'PUT':
        try:
            acknowledge_alert(uuid)
            socket.emit('updateAlerts')
            return jsonify(status='ok')
        except Alert.DoesNotExist:
            return jsonify(status='No such alert'), 404

    elif request.method == 'DELETE':
        try:
            uuid = request.args['uuid']
            remove_alert(uuid)
            socket.emit('updateAlerts')
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
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']

    user = authenticate_user(username, password)

    if user is not None:
        remember = request.form.get('remember', False) == 'on'
        login_user(user, remember=remember)
        return redirect(request.args.get('next', '/'))
    else:
        flash('Wrong username/password', 'alert-danger')
        return render_template('login.html')


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
    flash('You are ready for shutdown!', 'alert-success')
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
    flash('Dummy alert sent!', 'alert-success')
    return redirect('/')


@app.route('/dummyAlert', methods=['GET'])
def get_dummy_alert():
    dummy_alerts = dict(zip(
        app.dummy_alerts.keys(),
        map(str, app.dummy_alerts.values())
    ))
    return jsonify(dummy_alerts)


@app.route('/shifthelperHeartbeat', methods=['POST'])
@basic_auth.login_required
def update_shifthelper_online_time():
    app.heartbeats['shifthelperHeartbeat'] = datetime.utcnow()
    socket.emit('updateHeartbeats')
    return jsonify(app.heartbeats)


@app.route('/heartbeatMonitor', methods=['POST'])
@basic_auth.login_required
def update_heartbeat_monitor_last_check():
    app.heartbeats['heartbeatMonitor'] = datetime.utcnow()
    socket.emit('updateHeartbeats')
    return jsonify(app.heartbeats)


@app.route('/heartbeats')
def get_heartbeats():
    return jsonify(app.heartbeats)
