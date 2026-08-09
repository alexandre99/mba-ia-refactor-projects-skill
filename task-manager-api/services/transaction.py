from utils.errors import ApplicationError


def commit_or_error(unit_of_work, message):
    try:
        unit_of_work.commit()
    except Exception as exc:
        unit_of_work.rollback()
        raise ApplicationError(message, 500) from exc
