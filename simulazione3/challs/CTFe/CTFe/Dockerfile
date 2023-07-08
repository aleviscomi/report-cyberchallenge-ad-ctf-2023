# these two are in common for all the chalenges.
# We need to install some packets in order to "simplify" some challenges
# add php7.4-mysqli if php don't found the mysqli extension
FROM ubuntu:20.04
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y wget curl netcat \
    && DEBIAN_FRONTEND="noninteractive" apt-get install -y nginx supervisor python3 python3-pip php7.4 socat php7.4-sqlite php7.4-mysqli

RUN useradd -ms /bin/null web 

COPY ./src/requirements.txt /srv/app/
RUN pip3 install --no-cache-dir -r /srv/app/requirements.txt 

COPY config/nginx.conf /etc/nginx/nginx.conf
COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf


COPY ./src /srv/app/
COPY config/uwsgi.ini /srv/app/

ENV UWSGI_INI /srv/app/uwsgi.ini

WORKDIR /srv/app/

EXPOSE 80