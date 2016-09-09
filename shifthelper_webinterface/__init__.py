from flask import Flask, jsonify, render_template, redirect
from flask_socketio import SocketIO
from flask import request
from flask_ldap3_login.forms import LDAPLoginForm
from flask_login import login_user, login_required, logout_user
import logging
import json
import os

from .authentication import login_manager, ldap_manager

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']
app.alerts = {}

login_manager.init_app(app)
ldap_manager.init_app(app)
socket = SocketIO(app)


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


@app.route('/alerts', methods=['GET', 'POST'])
def alerts():
    if request.method == 'POST':

        alert = request.args.to_dict()

        alert['level'] = logging.getLevelName(int(alert['level']))
        alert['acknowledged'] = False

        key = alert['uuid']
        app.alerts[key] = alert

        update_clients()

        return jsonify(status='ok')

    elif request.method == 'GET':
        return jsonify(list(app.alerts.values()))


@app.route('/alerts/<uuid>', methods=['PUT', 'DELETE', 'GET'])
@login_required
def alert(uuid):

    if request.method == 'GET':
        try:
            return jsonify(app.alerts[uuid])
        except KeyError:
            return jsonify(status='No such alert'), 404

    elif request.method == 'PUT':
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


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/')
