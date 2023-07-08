const { Router } = require('express');
const db = require('../db');
const asyncWrapper = require('./express-async-wrapper');
const HttpError = require('./http-error');

const app = Router();

// Display name and prices of products
app.get(
  '/',
  asyncWrapper(async (req, res) => {
    const offset = req.query.offset ? parseInt(req.query.offset, 10) : 0;
    const { rows } = await db.query(
      'SELECT * FROM "products" ORDER BY id DESC OFFSET $1 LIMIT 10',
      [offset]
    );

    res.json(rows);
  })
);

// Admin: create a product
app.post(
  '/create',
  asyncWrapper(async (req, res) => {
    if (req.session.admin !== true) {
      throw new HttpError(401, 'Unauthorized');
    }

    const { name, price, secret } = req.body;
    const {rows: [{id}]} =  await db.query('INSERT INTO "products" (name, price, secret) VALUES ($1, $2, $3) RETURNING id', [
      name,
      price,
      secret
    ]);

    res.json({id});
  })
);

// User: view a product if the user have enough fidelity coins
app.post(
  '/view',
  asyncWrapper(async (req, res) => {
    if (req.session.userId === undefined) {
      throw new HttpError(401, 'Unauthorized');
    }

    const { productId, price } = req.body;
    const {
      rows: [product]
    } = await db.query('SELECT * FROM "products" WHERE id = $1', [productId]);

    if (!product) {
      throw new HttpError(404, 'Product not found');
    }

    const {
      rows: [user]
    } = await db.query('SELECT * FROM "users" WHERE id = $1', [req.session.userId]);

    if (user.coins < price) {
      throw new HttpError(400, 'You need more fidelity coins to view this product');
    }

    res.json({
      secret: product.secret
    });
  })
);

module.exports = app;
