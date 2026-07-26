class CheckoutRepository {
    constructor(db) {
        this.db = db;
    }

    createEnrollment(userId, courseId) {
        return this.db.run(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId]
        );
    }

    createPayment(enrollmentId, amount, status) {
        return this.db.run(
            'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
            [enrollmentId, amount, status]
        );
    }

    recordAudit(action) {
        return this.db.run(
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            [action]
        );
    }
}

module.exports = CheckoutRepository;
