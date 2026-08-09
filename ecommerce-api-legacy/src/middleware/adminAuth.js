function requireAdminToken(expectedToken) {
    return (req, res, next) => {
        if (!expectedToken || req.get('x-admin-token') !== expectedToken) {
            return res.status(401).send('Unauthorized');
        }
        return next();
    };
}

module.exports = requireAdminToken;
