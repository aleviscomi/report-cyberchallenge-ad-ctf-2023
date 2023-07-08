const express = require('express');
const session = require('express-session');
const users = require('./users');
const products = require('./products');
const giftCards = require('./gift-cards');

const app = express.Router();
app.use(
  session({
    resave: true,
    saveUninitialized: true,
    secret: 'secret',
    store: new session.MemoryStore()
  })
);
app.use(express.json());

app.use('/users', users);
app.use('/products', products);
app.use('/giftCards', giftCards);

app.use((_req, res) => {
  res.status(404).json({ error: 'Not found' });
});

module.exports = app;
