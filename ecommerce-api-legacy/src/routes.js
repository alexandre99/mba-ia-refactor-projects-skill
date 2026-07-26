const express = require('express');
const requireAdminToken = require('./middleware/adminAuth');

function createRoutes({ checkoutController, reportController, userController, adminToken }) {
    const router = express.Router();
    const adminOnly = requireAdminToken(adminToken);

    router.post('/api/checkout', checkoutController.create.bind(checkoutController));
    router.get('/api/admin/financial-report', reportController.financialReport.bind(reportController));
    router.delete('/api/users/:id', adminOnly, userController.delete.bind(userController));

    return router;
}

module.exports = createRoutes;
