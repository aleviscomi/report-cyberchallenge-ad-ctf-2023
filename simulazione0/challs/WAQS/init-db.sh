#!/bin/sh
DB_NAME=air_quality_db

psql $DB_NAME  <<EOF
CREATE TABLE IF NOT EXISTS air_quality (
        id              integer PRIMARY KEY,
        PM_10           integer,
        PM_25           integer,
        CO              integer,
        NO_2            integer,
        SO_2            integer,
        O_3             integer,
        location        TEXT,
        secret_comment  TEXT,
        password        TEXT,
        prng_seed       integer,
        ts              timestamp DEFAULT CURRENT_TIMESTAMP
);
EOF

psql $DB_NAME  <<EOF
CREATE TABLE IF NOT EXISTS bug_report (
        id              SERIAL PRIMARY KEY,
        name            TEXT,
        description     TEXT,
        ts              timestamp DEFAULT CURRENT_TIMESTAMP
);
EOF
sed -i 's/host all all all md5//g' /var/lib/postgresql/data/pg_hba.conf

echo "host      air_quality_db  all     172.31.0.10/16    trust" >> /var/lib/postgresql/data/pg_hba.conf
echo "host      all             all     all               md5" >> /var/lib/postgresql/data/pg_hba.conf

service postgresql restart
