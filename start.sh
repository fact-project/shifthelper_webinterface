#!/bin/bash

service nginx start
uwsgi --ini /var/www/shifthelper-www/shifthelper_uwsgi.ini
