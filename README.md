# shifthelper_webinterface
The webinterface for the shifthelper

## Technology stack

We are using

* twitter bootstrap for responsivness (make it look good on mobile)
* vue to make it reactive (basically update things without refresh)
* socketio for the websocket (notifications from the server to the clients)


## Local Testing without docker for the webinterface

The webinterface will use a sqlite database if the flask debug option is used.

Install the requirements
```
$ pip install -e requirements.txt
```

```
$ export SHIFTHELPER_CONFIG=/path/to/config/json
$ export FLASK_DEBUG=true
$ export FLASK_APP=shifthelper_webinterface/__init__.py
$ flask run
```
