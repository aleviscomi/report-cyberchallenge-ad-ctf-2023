const { Router } = require('express');
const Postgres = require('pg');
const HttpError = require('./http-error');
const asyncWrapper = require('./express-async-wrapper');
const db = require('../db');
const GiftCard = require('../utils/gift-card');

const app = Router();

// User: register
app.post(
  '/register',
  asyncWrapper(async (req, res) => {
    const { username, password } = req.body;

    if (username === 'admin') {
      throw new HttpError(400, 'Username already exists');
    }

    if (username.length < 5) {
      throw new HttpError(400, 'Username must be at least 5 characters');
    } else if (username.length > 25) {
      throw new HttpError(400, 'Username must be at most 25 characters');
    }

    try {
      const {
        rows: [{ id }]
      } = await db.query('INSERT INTO "users" (username, password, coins) VALUES ($1, $2, 0) RETURNING id', [
        username,
        password
      ]);

      req.session.userId = id;
    } catch (e) {
      if (e instanceof Postgres.DatabaseError && e.code == '23505') {
        throw new HttpError(400, 'Username already exists');
      }
    }

    res.json({ giftCard: GiftCard.encode(username, 10) });
  })
);

// Login
app.post(
  '/login',
  asyncWrapper(async (req, res) => {
    const { username, password } = req.body;

    if (username === 'admin') {
      // DO NOT CHANGE ADMIN_PASSWORD, IT'S NEEDED BY CHECKER
      if (password === process.env.ADMIN_PASSWORD) {
        req.session.admin = true;
      } else {
        throw new HttpError(400, 'Invalid username or password');
      }
    } else {
      const {
        rows: [user]
      } = await db.query('SELECT * FROM "users" WHERE username = $1', [username]);

      if (!user) {
        throw new HttpError(400, 'Invalid username or password');
      }

      req.session.userId = user.id;
    }

    res.json({})
  })
);

// Logout
app.get('/logout', (req, res) => {
  req.session.destroy();
  res.json({});
});

// User: view fidelity points balance
app.get(
  '/balance',
  asyncWrapper(async (req, res) => {
    if (req.session.userId === undefined) {
      throw new HttpError(401, 'Unauthorized');
    }

    const {
      rows: [{ coins }]
    } = await db.query('SELECT * FROM "users" WHERE id = $1', [req.session.userId]);

    res.json({ coins });
  })
);

module.exports = app;
