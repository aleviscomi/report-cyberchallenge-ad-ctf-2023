require('dotenv').config();
const express = require('express');
const expressListRoutes = require('express-list-routes');
const HttpError = require('./api/http-error');
const db = require('./db');
const api = require('./api');

const app = express();

app.use('/api', api);
expressListRoutes(api, { prefix: '/api' });

app.use((err, _req, res, _next) => {
  if (err instanceof HttpError) {
    res.status(err.code).json({ message: err.message });
  } else {
    console.error(err);
    res.status(500).json(err);
  }
});

app.use((_req, res) => {
  res.status(404).end('Are you looking for the frontend? Too bad, we ran out of budget');
});

(async () => {
  await db.dbConnect();

  app.listen(8080);
  console.log('Listening on 8080');
})();
