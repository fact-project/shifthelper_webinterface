#!/bin/bash
service nginx start
runuser  -m fact -c "python run.py"
