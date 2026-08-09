class UserController {
    constructor(userService) {
        this.userService = userService;
    }

    async delete(req, res) {
        try {
            return res.send(await this.userService.delete(req.params.id));
        } catch (error) {
            console.error(error);
            return res.status(500).send('Erro DB');
        }
    }
}

module.exports = UserController;
