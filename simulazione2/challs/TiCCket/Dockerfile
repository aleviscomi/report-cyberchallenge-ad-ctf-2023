FROM ubuntu:20.04

RUN apt-get update \
 && apt-get install -y socat

WORKDIR /service

COPY ./server .
RUN chmod +x ./server

CMD ["/usr/bin/socat", "TCP-LISTEN:1337,fork,reuseaddr,bind=0.0.0.0", "EXEC:./server"]
