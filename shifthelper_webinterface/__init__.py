from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO
from flask import request
import logging
import json

app = Flask(__name__)
app.messages = []

socket = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html', messages=app.messages)


@app.route('/alerts', methods=['GET', 'POST'])
def alerts():
    if request.method == 'POST':

        message = request.args.to_dict()
        message['level'] = logging.getLevelName(int(message['level']))
        message['acknowledged'] = False
        app.messages.append(message)

        socket.emit('update', json.dumps(app.messages))

        return jsonify(status='ok')

    elif request.method == 'GET':
        return jsonify(app.messages)
