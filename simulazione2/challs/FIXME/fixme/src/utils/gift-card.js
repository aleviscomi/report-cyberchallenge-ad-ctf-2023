const crypto = require('crypto');

module.exports.encode = (user, amount) => {
  const payload = `${user}-${amount}`;
  const signature = crypto
    .createHmac('sha256', process.env.GIFT_CARD_SECRET)
    .update(payload)
    .digest('hex');
  const data = `${payload}|${signature}`;
  return Buffer.from(data).toString('base64');
};

module.exports.decode = (giftCard) => {
  const data = Buffer.from(giftCard, 'base64').toString();
  const [payload, signature] = data.split('|');
  const expectedSignature = crypto
    .createHmac('sha256', process.env.GIFT_CARD_SECRET)
    .update(payload)
    .digest('hex');
  if (signature !== expectedSignature) throw new Error('Invalid gift card');
  const [user, amount] = payload.split('-');
  return { user, amount };
};
