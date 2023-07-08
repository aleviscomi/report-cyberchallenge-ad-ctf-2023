FROM ubuntu:20.04

RUN apt update \
    && apt install -y python3 python3-dev socat python3-pip gcc g++ make libffi-dev

RUN pip3 install pycryptodome

RUN useradd --no-create-home --shell /bin/false --uid 1000 --user-group srv

ADD app /service/

WORKDIR /service/

RUN mkdir data
RUN chmod +x service.py
RUN chmod -R 777 data

USER srv

ENTRYPOINT socat -d TCP-LISTEN:3000,reuseaddr,fork EXEC:'timeout -k 5 30 python3 -u service.py'
