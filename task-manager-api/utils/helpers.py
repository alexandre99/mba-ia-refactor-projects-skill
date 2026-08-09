import logging
import uuid

from utils import validation as rules
from utils.errors import ApplicationError

DEFAULT_COLOR = rules.DEFAULT_COLOR
DEFAULT_PRIORITY = rules.DEFAULT_PRIORITY
MAX_TITLE_LENGTH = rules.MAX_TITLE_LENGTH
MIN_PASSWORD_LENGTH = rules.MIN_PASSWORD_LENGTH
MIN_TITLE_LENGTH = rules.MIN_TITLE_LENGTH
VALID_ROLES = rules.VALID_ROLES
VALID_STATUSES = rules.VALID_STATUSES
validate_email = rules.validate_email


def format_date(date_obj):
    return str(date_obj) if date_obj else None


def calculate_percentage(part, total):
    return 0 if total == 0 else round((part / total) * 100, 2)


def sanitize_string(value):
    return value.strip() if value else value


def generate_id():
    return str(uuid.uuid4())


def log_action(action, details=None):
    logging.getLogger(__name__).info("action=%s details=%s", action, details)


def parse_date(date_string):
    try:
        return rules.parse_date(date_string)
    except ApplicationError:
        return None


def is_valid_color(color):
    return bool(color and len(color) == 7 and color[0] == "#")


def process_task_data(data, existing_task=None):
    try:
        return rules.normalize_task_payload(data, partial=existing_task is not None), None
    except ApplicationError as exc:
        return None, exc.message
