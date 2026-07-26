const nodeEnv = process.env.NODE_ENV || 'development';
const databasePath = process.env.DATABASE_PATH || (nodeEnv === 'production' ? '' : ':memory:');

if (nodeEnv === 'production' && (!databasePath || databasePath === ':memory:')) {
    throw new Error('DATABASE_PATH must be configured with durable storage in production');
}

const config = {
    port: Number(process.env.PORT || 3000),
    databasePath,
    adminToken: process.env.ADMIN_TOKEN || ''
};

module.exports = config;
