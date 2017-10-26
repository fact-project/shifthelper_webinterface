FROM continuumio/miniconda3

EXPOSE 80
EXPOSE 443

RUN apt-get update -qq \
	&& apt-get install -y locales libcairo2 unzip nginx ca-certificates\
	&& echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
	&& locale-gen

ENV LC_ALL="en_US.UTF-8"
ENV LANG="en_US.UTF-8"

RUN conda install python=3.5 \
  && conda install -y -q flask pandas pymysql sqlalchemy requests \
  && conda install -y -q -c conda-forge uwsgi \
  && pip install flask_login flask_ldap3_login flask_socketio \
  twilio==5.7.0 telepot flask_httpauth peewee eventlet \
  gunicorn

RUN rm /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/conf.d/shifthelper_nginx.conf

RUN useradd -m fact

COPY start.sh run.py /home/fact/
COPY shifthelper_webinterface /home/fact/shifthelper_webinterface
RUN chown -R fact:fact /home/fact/shifthelper_webinterface \
	&& chmod +x /home/fact/start.sh

WORKDIR /home/fact/
CMD ./start.sh

