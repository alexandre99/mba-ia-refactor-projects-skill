class ApplicationError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(ApplicationError):
    def __init__(self, message):
        super().__init__(message, 404)


class ConflictError(ApplicationError):
    def __init__(self, message):
        super().__init__(message, 409)


class AuthenticationError(ApplicationError):
    def __init__(self, message="Credenciais inválidas"):
        super().__init__(message, 401)
