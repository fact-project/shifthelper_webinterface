from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO
from flask import request
import logging
import json

app = Flask(__name__)
app.alerts = {}

socket = SocketIO(app)


def remove_alert(uuid):
    app.alerts.pop(uuid)


def update_clients():
    alerts = list(app.alerts.values())
    alerts.sort(key=lambda m: m['timestamp'], reverse=True)
    socket.emit('update', json.dumps(alerts))


@app.route('/')
def index():
    update_clients()
    return render_template('index.html')


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
