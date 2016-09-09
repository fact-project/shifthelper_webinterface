from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO
from flask import request
import logging
import json

app = Flask(__name__)
app.messages = {}

socket = SocketIO(app)


def remove_alert(uuid):
    app.messages.pop(uuid)


def update_clients():
    messages = list(app.messages.values())
    messages.sort(key=lambda m: m['timestamp'], reverse=True)
    socket.emit('update', json.dumps(messages))


@app.route('/')
def index():
    update_clients()
    return render_template('index.html')


@app.route('/alerts', methods=['GET', 'POST'])
def alerts():
    if request.method == 'POST':

        message = request.args.to_dict()

        message['level'] = logging.getLevelName(int(message['level']))
        message['acknowledged'] = False

        key = message['uuid']
        app.messages[key] = message

        update_clients()

        return jsonify(status='ok')

    elif request.method == 'GET':
        return jsonify(list(app.messages.values()))


@app.route('/alerts/<uuid>', methods=['PUT', 'DELETE', 'GET'])
def alert(uuid):

    if request.method == 'GET':
        try:
            return jsonify(app.messages[uuid])
        except KeyError:
            return jsonify(status='No such alert'), 404

    elif request.method == 'PUT':
        try:
            app.messages[uuid]['acknowledged'] = True
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
