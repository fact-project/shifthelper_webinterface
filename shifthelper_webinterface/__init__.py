from flask import Flask, jsonify, render_template
from flask import request
import logging

app = Flask(__name__)
app.messages = []


@app.route('/')
def index():
    return render_template('index.html', messages=app.messages)


@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'POST':

        message = request.args.to_dict()
        message['level'] = logging.getLevelName(int(message['level']))
        message['acknowledged'] = False
        app.messages.append(message)

        return jsonify(status='ok')

    elif request.method == 'GET':
        return jsonify(app.messages)
