CREATE DATABASE CApp;

USE CApp;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(30) NOT NULL,
    password VARCHAR(150) NOT NULL,
    uuid VARCHAR(36),
    INDEX username_ind (`username`)
);

CREATE TABLE vm (
    owner VARCHAR(30) PRIMARY KEY,
    FOREIGN KEY (owner) REFERENCES users(username)
);

CREATE TABLE env_var (
    vm VARCHAR(30),
    name VARCHAR(20),
    value VARCHAR(500),
    FOREIGN KEY (vm) REFERENCES vm(owner),
    PRIMARY KEY(vm, name)
);