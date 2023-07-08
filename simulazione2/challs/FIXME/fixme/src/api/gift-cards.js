const { Router } = require('express');
const asyncWrapper = require('./express-async-wrapper');
const GiftCard = require('../utils/gift-card');
const db = require('../db');
const HttpError = require('./http-error');

const app = Router();

// Admin: create gift card
app.post(
  '/create',
  asyncWrapper(async (req, res) => {
    if (req.session.admin !== true) {
      throw new HttpError(401, 'Unauthorized');
    }

    const { user, amount } = req.body;

    return res.json({ giftCard: GiftCard.encode(user, amount) });
  })
);

// User: redeem gift card
app.post(
  '/redeem',
  asyncWrapper(async (req, res) => {
    if (req.session.userId === undefined) {
      throw new HttpError(401, 'Unauthorized');
    }

    const { giftCard } = req.body;

    const { user, amount } = GiftCard.decode(giftCard);

    if (user !== '*') {
      const {
        rows: [{ username }]
      } = await db.query('SELECT * FROM "users" WHERE id = $1', [req.session.userId]);

      if (user !== username) {
        throw new HttpError(400, 'This gift card is not for you');
      }
    }

    await db.query('UPDATE "users" SET coins = coins + $2 WHERE id = $1', [
      req.session.userId,
      amount
    ]);

    res.json({});
  })
);

module.exports = app;
