from functools import wraps

from flask import current_app, g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from repositories.user_repository import UserRepository


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="task-manager-api-access")


def create_access_token(user):
    return _serializer().dumps({"user_id": user.id})


def current_user():
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        return None
    try:
        payload = _serializer().loads(token, max_age=current_app.config["TOKEN_MAX_AGE"])
    except (BadSignature, SignatureExpired, TypeError, ValueError):
        return None
    return UserRepository().get(payload.get("user_id"))


def require_admin(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if user is None:
            return jsonify({"error": "Autenticação necessária"}), 401
        if not user.active or not user.is_admin():
            return jsonify({"error": "Acesso negado"}), 403
        g.current_user = user
        return view(*args, **kwargs)

    return wrapped
