const config = {
    port: Number(process.env.PORT || 3000),
    databasePath: process.env.DATABASE_PATH || ':memory:',
    adminToken: process.env.ADMIN_TOKEN || ''
};

module.exports = config;
