const { MESSAGES } = require('../constants');

class UserService {
    constructor(userRepository) {
        this.userRepository = userRepository;
    }

    async delete(id) {
        await this.userRepository.deleteById(id);
        return MESSAGES.USER_DELETED;
    }
}

module.exports = UserService;
