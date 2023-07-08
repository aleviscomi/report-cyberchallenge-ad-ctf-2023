FROM ubuntu:focal
LABEL Name=/WAQS-service Version=0.0.1

ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8


RUN echo "+ Installing dependencies..."
RUN apt update
RUN apt-get -y install build-essential && apt-get -y install clang-8 socat


RUN echo  "+ postgress stuff"

RUN apt-get -y install  lsb-release wget 
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get update
RUN apt-get -y install libpq-dev

RUN echo  "+ adding binary"
ADD ./WAQS /WAQS
RUN chmod +x /WAQS

EXPOSE 12345
