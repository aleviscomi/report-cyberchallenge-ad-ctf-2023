FROM ubuntu:18.04

RUN apt update && apt upgrade && apt install -y build-essential python3-dev python3-pip libssl-dev uwsgi uwsgi-plugin-python3

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN groupadd -r crashair && useradd -M -r -g crashair crashair

COPY --chown=crashair:crashair src /app

WORKDIR /app

USER crashair

CMD ["python3", "main.py"]