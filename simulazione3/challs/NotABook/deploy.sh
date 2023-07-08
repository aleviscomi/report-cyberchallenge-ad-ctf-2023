#!/bin/bash

if [[ ! -f ".env" ]]
then
    SECRET_KEY=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 16)
    echo "SECRET_KEY=${SECRET_KEY}" > .env
fi

docker compose up --build --remove-orphans -d
