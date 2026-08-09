const express = require('express');
const config = require('./config');
const SqliteDatabase = require('./infrastructure/database');
const initializeDatabase = require('./infrastructure/initializeDatabase');
const CourseRepository = require('./repositories/courseRepository');
const UserRepository = require('./repositories/userRepository');
const CheckoutRepository = require('./repositories/checkoutRepository');
const ReportRepository = require('./repositories/reportRepository');
const CheckoutService = require('./services/checkoutService');
const ReportService = require('./services/reportService');
const UserService = require('./services/userService');
const CheckoutController = require('./controllers/checkoutController');
const ReportController = require('./controllers/reportController');
const UserController = require('./controllers/userController');
const createRoutes = require('./routes');

async function createApp({ database } = {}) {
    const db = database || new SqliteDatabase(config.databasePath);
    await initializeDatabase(db);

    const userRepository = new UserRepository(db);
    const checkoutService = new CheckoutService({
        courseRepository: new CourseRepository(db),
        userRepository,
        checkoutRepository: new CheckoutRepository(db),
        cache: new Map(),
        transaction: db.transaction.bind(db)
    });
    const reportService = new ReportService(new ReportRepository(db));
    const userService = new UserService(userRepository);

    const app = express();
    app.use(express.json());
    app.use(createRoutes({
        checkoutController: new CheckoutController(checkoutService),
        reportController: new ReportController(reportService),
        userController: new UserController(userService),
        adminToken: config.adminToken
    }));
    app.locals.database = db;
    return { app, db };
}

module.exports = createApp;
