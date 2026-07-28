import re
from datetime import datetime

from utils.errors import ApplicationError

VALID_STATUSES = ["pending", "in_progress", "done", "cancelled"]
VALID_ROLES = ["user", "admin", "manager"]
MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MIN_PASSWORD_LENGTH = 4
DEFAULT_PRIORITY = 3
DEFAULT_COLOR = "#000000"


def validate_email(email):
    return bool(email and re.match(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$", email))


def parse_date(date_string, message="Formato de data inválido"):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")  # noqa: DTZ007 - SQLite contract uses naive UTC datetimes
    except (TypeError, ValueError) as exc:
        raise ApplicationError(message, 400) from exc


def normalize_task_payload(data, partial=False):
    if not isinstance(data, dict) or not data:
        raise ApplicationError("Dados inválidos", 400)

    result = {}
    if not partial or "title" in data:
        title = data.get("title")
        if not title:
            raise ApplicationError("Título é obrigatório" if not partial else "Título não pode ser vazio")
        if len(title) < MIN_TITLE_LENGTH:
            raise ApplicationError("Título muito curto")
        if len(title) > MAX_TITLE_LENGTH:
            raise ApplicationError("Título muito longo")
        result["title"] = title

    if "description" in data:
        result["description"] = data.get("description")

    if not partial:
        result["status"] = data.get("status", "pending")
        result["priority"] = data.get("priority", DEFAULT_PRIORITY)
    else:
        if "status" in data:
            result["status"] = data["status"]
        if "priority" in data:
            result["priority"] = data["priority"]

    if "status" in result and result["status"] not in VALID_STATUSES:
        raise ApplicationError("Status inválido")
    if "priority" in result:
        try:
            priority = int(result["priority"])
        except (TypeError, ValueError) as exc:
            raise ApplicationError("Prioridade inválida") from exc
        if not 1 <= priority <= 5:
            raise ApplicationError("Prioridade deve ser entre 1 e 5")
        result["priority"] = priority

    for field in ("user_id", "category_id"):
        if field in data:
            result[field] = data[field]

    if "due_date" in data:
        if data["due_date"]:
            message = "Formato de data inválido. Use YYYY-MM-DD" if not partial else "Formato de data inválido"
            result["due_date"] = parse_date(data["due_date"], message)
        else:
            result["due_date"] = None

    if "tags" in data:
        tags = data["tags"]
        result["tags"] = ",".join(tags) if isinstance(tags, list) else tags

    return result


def validate_user_payload(data, partial=False):
    if not isinstance(data, dict) or not data:
        raise ApplicationError("Dados inválidos", 400)

    result = {}
    if not partial or "name" in data:
        if not data.get("name"):
            raise ApplicationError("Nome é obrigatório")
        result["name"] = data["name"]

    if not partial or "email" in data:
        email = data.get("email")
        if not email:
            raise ApplicationError("Email é obrigatório")
        if not validate_email(email):
            raise ApplicationError("Email inválido")
        result["email"] = email

    if not partial or "password" in data:
        password = data.get("password")
        if not password:
            raise ApplicationError("Senha é obrigatória")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ApplicationError("Senha deve ter no mínimo 4 caracteres" if not partial else "Senha muito curta")
        result["password"] = password

    if "role" in data:
        if data["role"] not in VALID_ROLES:
            raise ApplicationError("Role inválido")
        result["role"] = data["role"]
    if "active" in data:
        result["active"] = data["active"]
    return result
