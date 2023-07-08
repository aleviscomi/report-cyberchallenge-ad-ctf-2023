FROM ubuntu:20.04

RUN apt-get update \
    && DEBIAN_FRONTEND="noninteractive" apt-get install -y build-essential libseccomp-dev

COPY httpd /usr/src/httpd

WORKDIR /usr/src/httpd
RUN make all


FROM ubuntu:20.04
RUN apt-get update \
    && apt-get upgrade -y \
    && DEBIAN_FRONTEND="noninteractive" apt-get install -y python3 python3-pip supervisor

RUN useradd -ms /bin/null web && mkdir /srv/uploads && chown web /srv/uploads

COPY requirements.txt /srv/app/
RUN pip3 install --no-cache-dir -r /srv/app/requirements.txt 

COPY --from=0 /usr/src/httpd/bin/httpd /srv/httpd
COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY cgi /srv/app/cgi
COPY cgi/static/ /srv/static

WORKDIR /srv/app/cgi