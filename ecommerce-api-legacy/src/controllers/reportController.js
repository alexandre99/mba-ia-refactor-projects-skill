class ReportController {
    constructor(reportService) {
        this.reportService = reportService;
    }

    async financialReport(req, res) {
        try {
            return res.json(await this.reportService.generate());
        } catch (error) {
            console.error(error);
            return res.status(500).send('Erro DB');
        }
    }
}

module.exports = ReportController;
