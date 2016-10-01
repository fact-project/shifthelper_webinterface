# shifthelper_webinterface
The webinterface for the shifthelper


# how to start:

 - clone
 - cd into 
 - `docker build .`
```
docker run \
  --restart=always \
  -p 80:80 \
  -p 443:443 \
  -v $HOME/shifthelper-config:/config \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -e SHIFTHELPER_CONFIG=/config/webservice.json \
  --link shifthelper-mysql:mysql \
  --name=shifthelper_webinterface \
  -d -t shifthelper_webinterface
```
