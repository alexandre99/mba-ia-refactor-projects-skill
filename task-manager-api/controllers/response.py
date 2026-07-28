from flask import current_app, jsonify

from utils.errors import ApplicationError


def execute(operation, success_status=200):
    try:
        return jsonify(operation()), success_status
    except ApplicationError as exc:
        return jsonify({"error": exc.message}), exc.status_code
    except Exception:
        current_app.logger.exception("Unhandled application error")
        return jsonify({"error": "Erro interno"}), 500
