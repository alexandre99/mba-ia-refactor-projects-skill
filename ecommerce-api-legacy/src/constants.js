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

module.exports = { PAYMENT_STATUS, MESSAGES };
