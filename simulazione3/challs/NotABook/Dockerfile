FROM ubuntu:20.04

RUN apt-get update && apt-get -y install socat python3 python3-pip

WORKDIR /app

COPY ./src/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY ./src .

ENV PYTHONUNBUFFERED=1

ENTRYPOINT socat -t 30 -T 30 -d TCP-LISTEN:1234,reuseaddr,fork EXEC:'./app.py ./data'
