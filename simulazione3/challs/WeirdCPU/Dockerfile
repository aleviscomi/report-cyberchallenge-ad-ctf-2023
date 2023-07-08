FROM ubuntu:20.04
RUN apt-get update \
  && apt-get upgrade -y \
  && DEBIAN_FRONTEND="noninteractive" apt-get install -y nginx supervisor python3 python3-pip
RUN pip3 install --no-cache-dir uWSGI

WORKDIR /app

COPY ./src/requirements.txt .
RUN pip3 install --no-cache-dir -r ./requirements.txt
COPY ./src .
COPY ./config/uwsgi.ini .

RUN useradd -ms /bin/null web
COPY config/nginx.conf /etc/nginx/nginx.conf
COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENV UWSGI_INI /app/uwsgi.ini

CMD /usr/bin/supervisord
