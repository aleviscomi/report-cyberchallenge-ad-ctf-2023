const { Pool } = require('pg');

let retry_count = 10;

const postgres = new Pool({
  host: process.env.POSTGRES_HOST,
  database: process.env.POSTGRES_DB,
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  max: 20,
  idleTimeoutMillis: 10000
});

module.exports = postgres;

module.exports.dbConnect = async () => {
  if (--retry_count === 0) {
    return false;
  }

  try {
    const client = await postgres.connect();
    await client.query('SELECT NOW()');
    client.release();

    return true;
  } catch (error) {
    console.log('DB', error.toString());
    console.log('DB sync (connection) failed, retrying in 10 seconds');
    await new Promise((resolve) => {
      setTimeout(resolve, 5000);
    });
    return await module.exports.dbConnect();
  }
};
