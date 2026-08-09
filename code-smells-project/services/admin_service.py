import hmac

from errors import AuthorizationError, ValidationError
from repositories import admin_repository


_ALLOWED_QUERY = "SELECT COUNT(*) AS total FROM produtos"


def reset_database(provided_token, expected_token):
    if not expected_token or not provided_token or not hmac.compare_digest(
        provided_token, expected_token
    ):
        raise AuthorizationError()
    admin_repository.reset_database()


def execute_query(query):
    if not query:
        raise ValidationError("Query não informada")
    normalized = " ".join(query.strip().split())
    if normalized.casefold() != _ALLOWED_QUERY.casefold():
        raise ValidationError("Query não permitida")
    return admin_repository.count_products()
