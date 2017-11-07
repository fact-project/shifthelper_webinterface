# shifthelper_webinterface
The webinterface for the shifthelper

## Technology stack

We are using

* twitter bootstrap for responsivness (make it look good on mobile)
* react (without jsx) for rendering the alert table on the client side
* socketio for the websocket (new alerts pop up without refreshing the page)

React using pure javascript avoids a more complicated compilation step but 
results in more boilerplate code.
See
* https://reactjs.org/docs/introducing-jsx.html
* https://reactjs.org/docs/react-without-jsx.html


## Local Testing without docker for the webinterface

Install the requirements
```
pip install -e requirements.txt
```

Start a mysql instance for the webservice,
either setup a local mysql database or use docker with this command:
```
$ docker run --restart=always \
	-d \
	-e MYSQL_RANDOM_ROOT_PASSWORD=yes \
	-e MYSQL_DATABASE=shifthelper \
	-e MYSQL_USER=<user> \
	-e MYSQL_PASSWORD=<password> \
	--name=shifthelper_mysql \
	mysql
```

Adapt the database settings in the config file to reflect your local db setup,
then run

```
export SHIFTHELPER_CONFIG=/path/to/config/json
gunicorn -k eventlet -b 127.0.0.1:5000 shifthelper_webinterface:app
```
