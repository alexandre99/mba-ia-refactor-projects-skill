const { PAYMENT_STATUS } = require('../constants');

class ReportService {
    constructor(reportRepository) {
        this.reportRepository = reportRepository;
    }

    async generate() {
        const rows = await this.reportRepository.listCourseRows();
        const report = new Map();

        for (const row of rows) {
            if (!report.has(row.course_id)) {
                report.set(row.course_id, {
                    course: row.course_title,
                    revenue: 0,
                    students: []
                });
            }

            const course = report.get(row.course_id);
            if (row.enrollment_id === null || row.enrollment_id === undefined) continue;
            if (row.payment_status === PAYMENT_STATUS.PAID) {
                course.revenue += Number(row.paid_amount || 0);
            }
            course.students.push({
                student: row.student_name || 'Unknown',
                paid: Number(row.paid_amount || 0)
            });
        }

        return Array.from(report.values());
    }
}

module.exports = ReportService;
