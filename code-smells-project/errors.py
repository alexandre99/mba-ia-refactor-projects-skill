class ApplicationError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {"erro": message}


class ValidationError(ApplicationError):
    pass


class AuthorizationError(ApplicationError):
    def __init__(self, message="Acesso não autorizado"):
        super().__init__(message, status_code=403)
