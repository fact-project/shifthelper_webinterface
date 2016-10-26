# shifthelper_webinterface
The webinterface for the shifthelper


# how to start:

 - clone
 - cd into 

# 
Build the container:
```
$ docker build -t shifthelper_webinterface .`
```

Start a mysql instance for our webservice
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
Start the shifthelper container

```
$ docker run \
	--restart=always \  # restart on boot
	-d \ # run as daemon
	-p 80:80 -p 443:443 \ # expose http and https ports
	-v $(HOME)/shifthelper-config:/config \ # mount config path
	-v /etc/letsencrypt:/etc/letsencrypt \  # mount letsencrypt path
	-e SHIFTHELPER_CONFIG=/config/webservice.json \ # set config file oath
	--link shifthelper_mysql:mysql \ # connect the mysql container to this one
	-t shifthelper_webinterface
```
