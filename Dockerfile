FROM ubuntu:20.04

EXPOSE 80

RUN apt-get update -qq \
	&& apt-get install --no-install-recommends -y \
		locales libcairo2 unzip nginx netbase ca-certificates \
		python3 python3-pip python3-wheel python3-setuptools \
	&& echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
	&& locale-gen \
	&& rm -rf /var/lib/apt/lists/* \
	&& python3 -m pip install --no-cache poetry==1.0.5

ENV LC_ALL="en_US.UTF-8"
ENV LANG="en_US.UTF-8"



RUN rm /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/conf.d/shifthelper_nginx.conf

RUN useradd -m fact

WORKDIR /home/fact/
COPY pyproject.toml poetry.lock ./

# install production dependencies
RUN poetry config virtualenvs.create false \
	&& poetry install -E deploy --no-dev


COPY shifthelper_webinterface /home/fact/shifthelper_webinterface
COPY start.sh ./
RUN chown -R fact:fact /home/fact/shifthelper_webinterface \
	&& chmod +x /home/fact/start.sh

CMD ./start.sh
