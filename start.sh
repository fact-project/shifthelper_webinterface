#!/bin/bash
service nginx start
runuser  -m fact -c "python3 -m gunicorn.app.wsgiapp -k eventlet -b 127.0.0.1:5000 shifthelper_webinterface:app"
