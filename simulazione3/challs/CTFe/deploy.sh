#!/bin/bash

SECRET_FLASK=$(hexdump -vn16 -e'4/4 "%08X" 1 "\n"' /dev/urandom);
DB_PASSW=$(hexdump -vn16 -e'4/4 "%08X" 1 "\n"' /dev/urandom);

if [[ ! -f ".env" ]]
then
    echo "SECRET_FLASK=${SECRET_FLASK}" >> .env
    echo "DB_PASSW=${DB_PASSW}" >> .env
fi

docker compose up --build --remove-orphans -d
