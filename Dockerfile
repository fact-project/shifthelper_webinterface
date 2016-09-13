FROM ubuntu:16.04

RUN apt update && apt upgrade -y && apt install -y nginx ca-certificates curl bzip2
RUN locale-gen en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8

EXPOSE 80
EXPOSE 443

RUN curl https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
  -o miniconda.sh \
  && bash miniconda.sh -b -p /opt/miniconda/ \
  && echo 'export PATH=/opt/miniconda/bin:$PATH' > /etc/profile.d/conda.sh

ENV PATH /opt/miniconda/bin:$PATH

RUN conda install -y -q flask pandas \
  && conda install -y -q -c conda-forge uwsgi \
  && pip install flask_login flask_ldap3_login flask_socketio \
  twilio telepot flask_httpauth sqlalchemy pymysql

RUN rm /etc/nginx/sites-enabled/default \
  && mkdir /var/log/uwsgi && chown -R www-data:www-data /var/log/uwsgi \
  && mkdir /var/www/shifthelper-www && chown -R www-data:www-data /var/www/shifthelper-www \
  && ln -s /var/www/shifthelper-www/shifthelper_nginx.conf /etc/nginx/conf.d/


COPY shifthelper_nginx.conf /var/www/shifthelper-www/
COPY shifthelper_webinterface /var/www/shifthelper-www/shifthelper_webinterface
COPY shifthelper_uwsgi.ini /var/www/shifthelper-www/
COPY run.py /var/www/shifthelper-www/
RUN chown -R www-data:www-data /var/www/shifthelper-www


COPY start.sh .
CMD bash start.sh
