const ApplicationError = require('../errors/ApplicationError');
const { MESSAGES } = require('../constants');

class CheckoutController {
    constructor(checkoutService) {
        this.checkoutService = checkoutService;
    }

    async create(req, res) {
        const body = req.body || {};
        const { usr, eml, pwd, c_id: courseId, card } = body;
        if (!usr || !eml || !pwd || !courseId || !card) {
            return res.status(400).send(MESSAGES.BAD_REQUEST);
        }

        try {
            const result = await this.checkoutService.execute({
                name: usr,
                email: eml,
                password: pwd,
                courseId,
                card
            });
            return res.status(200).json(result);
        } catch (error) {
            if (error instanceof ApplicationError) {
                return res.status(error.statusCode).send(error.message);
            }
            console.error(error);
            return res.status(500).send('Erro interno');
        }
    }
}

module.exports = CheckoutController;
