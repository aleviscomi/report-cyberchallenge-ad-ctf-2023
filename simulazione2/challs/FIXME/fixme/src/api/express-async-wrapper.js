module.exports = (fn) => (req, res, next) => {
  (async () => {
    try {
      let nextCalled = false;
      const n = (err) => {
        nextCalled = true;
        next(err);
      };

      await fn(req, res, n);
      if (!nextCalled && !res.headersSent && !res.locals.doNotCallNext) n();
    } catch (error) {
      next(error);
    }
  })();
};
