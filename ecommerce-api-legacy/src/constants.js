const PAYMENT_STATUS = {
    PAID: 'PAID',
    DENIED: 'DENIED'
};

const MESSAGES = {
    BAD_REQUEST: 'Bad Request',
    COURSE_NOT_FOUND: 'Curso não encontrado',
    PAYMENT_DENIED: 'Pagamento recusado',
    CHECKOUT_SUCCESS: 'Sucesso',
    USER_DELETED: 'Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.'
};

const CHECKOUT_POLICY = {
    APPROVED_CARD_PREFIX: '4',
    CACHE_KEY_PREFIX: 'last_checkout_'
};

module.exports = { PAYMENT_STATUS, MESSAGES, CHECKOUT_POLICY };
