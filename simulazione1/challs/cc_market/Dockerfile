FROM cybersecnatlab/socaz:ubuntu-jammy

# Upgrade packages and install deps
RUN dpkg --add-architecture i386
RUN apt update
RUN apt install libc6-dbg:i386 -y

# Add binary
RUN echo  "[+] adding binary"
RUN mkdir /chall
ADD ./cc_market /chall/cc_market
RUN chmod +x /chall/cc_market
RUN mkdir /chall/data
WORKDIR /chall

EXPOSE 1337
