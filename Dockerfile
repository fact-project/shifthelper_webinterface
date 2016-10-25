FROM continuumio/miniconda3

EXPOSE 5000
RUN apt-get update -qq \
	&& apt-get install -y locales libcairo2 unzip\
	&& echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
	&& locale-gen

ENV LC_ALL="en_US.UTF-8"
ENV LANG="en_US.UTF-8"


RUN conda install -y -q flask pandas pymysql sqlalchemy requests \
  && conda install -y -q -c conda-forge uwsgi \
  && pip install flask_login flask_socketio \
  twilio telepot flask_httpauth 


COPY shifthelper_webinterface /var/www/shifthelper-www/shifthelper_webinterface
COPY run.py /var/www/shifthelper-www/
RUN chown -R www-data:www-data /var/www/shifthelper-www


WORKDIR /var/www/shifthelper-www
CMD python run.py
