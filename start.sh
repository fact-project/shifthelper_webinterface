#!/bin/bash
service nginx start
runuser  -m fact -c "gunicorn -k eventlet -b 127.0.0.1:5000 shifthelper_webinterface:app"
