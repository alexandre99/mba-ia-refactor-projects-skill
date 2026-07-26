const ApplicationError = require('../errors/ApplicationError');
const { PAYMENT_STATUS, MESSAGES } = require('../constants');
const { hashPassword } = require('../security/passwordHasher');

class CheckoutService {
    constructor({ courseRepository, userRepository, checkoutRepository, cache }) {
        this.courseRepository = courseRepository;
        this.userRepository = userRepository;
        this.checkoutRepository = checkoutRepository;
        this.cache = cache;
    }

    async execute({ name, email, password, courseId, card }) {
        const course = await this.courseRepository.findActiveById(courseId);
        if (!course) throw new ApplicationError(MESSAGES.COURSE_NOT_FOUND, 404);

        const paymentStatus = card.startsWith('4') ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
        if (paymentStatus === PAYMENT_STATUS.DENIED) {
            throw new ApplicationError(MESSAGES.PAYMENT_DENIED, 400);
        }

        let user = await this.userRepository.findByEmail(email);
        let userId = user && user.id;
        if (!userId) {
            const createdUser = await this.userRepository.create({
                name,
                email,
                passwordHash: hashPassword(password)
            });
            userId = createdUser.lastID;
        }

        const enrollment = await this.checkoutRepository.createEnrollment(userId, courseId);
        await this.checkoutRepository.createPayment(enrollment.lastID, course.price, paymentStatus);
        await this.checkoutRepository.recordAudit('Checkout curso ' + courseId + ' por ' + userId);
        this.cache.set('last_checkout_' + userId, course.title);

        return { msg: MESSAGES.CHECKOUT_SUCCESS, enrollment_id: enrollment.lastID };
    }
}

module.exports = CheckoutService;
