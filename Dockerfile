FROM ubuntu:16.04

EXPOSE 80
EXPOSE 443

RUN apt-get update -qq \
	&& apt-get install --no-install-recommends -y \
		locales libcairo2 unzip nginx netbase ca-certificates \
		python3 python3-pip python3-wheel python3-setuptools \
	&& echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
	&& locale-gen \
	&& rm -rf /var/lib/apt/lists/*

ENV LC_ALL="en_US.UTF-8"
ENV LANG="en_US.UTF-8"


RUN rm /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/conf.d/shifthelper_nginx.conf

RUN useradd -m fact

COPY start.sh run.py requirements.txt /home/fact/
RUN python3 -m pip install -r /home/fact/requirements.txt 

COPY shifthelper_webinterface /home/fact/shifthelper_webinterface
RUN chown -R fact:fact /home/fact/shifthelper_webinterface \
	&& chmod +x /home/fact/start.sh

WORKDIR /home/fact/
CMD ./start.sh

