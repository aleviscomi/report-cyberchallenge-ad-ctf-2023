CREATE DATABASE fixme;
GRANT ALL PRIVILEGES ON DATABASE fixme TO postgres;
\c fixme;

CREATE TABLE "users" (
  "id" SERIAL,
  "username" VARCHAR(255) UNIQUE,
  "password" VARCHAR(255),
  "coins" INTEGER
);

CREATE TABLE "products" (
  "id" SERIAL,
  "name" TEXT,
  "price" INTEGER,
  "secret" TEXT
);

