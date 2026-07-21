from werkzeug.security import check_password_hash, generate_password_hash

from repositories import user_repository


def list_users():
    return user_repository.list_users()


def get_user(user_id):
    return user_repository.get_user(user_id)


def create_user(data, tipo="cliente"):
    if not isinstance(data, dict) or not data:
        from errors import ValidationError

        raise ValidationError("Dados inválidos")

    nome = data.get("nome", "")
    email = data.get("email", "")
    senha = data.get("senha", "")
    if not nome or not email or not senha:
        from errors import ValidationError

        raise ValidationError("Nome, email e senha são obrigatórios")

    return user_repository.create_user(nome, email, generate_password_hash(senha), tipo)


def authenticate(email, password):
    user = user_repository.get_user_for_auth(email)
    if user is None or not check_password_hash(user["senha"], password):
        return None
    return {
        "id": user["id"],
        "nome": user["nome"],
        "email": user["email"],
        "tipo": user["tipo"],
    }
