const crypto = require('crypto');

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const derivedKey = crypto.scryptSync(password, salt, 64).toString('hex');
    return `scrypt$${salt}$${derivedKey}`;
}

function verifyPassword(password, storedValue) {
    if (!storedValue || !storedValue.startsWith('scrypt$')) return false;
    const [, salt, expectedKey] = storedValue.split('$');
    const actualKey = crypto.scryptSync(password, salt, 64).toString('hex');
    return crypto.timingSafeEqual(Buffer.from(actualKey, 'hex'), Buffer.from(expectedKey, 'hex'));
}

module.exports = { hashPassword, verifyPassword };
