from datetime import datetime, timezone


def utcnow():
    """Return a naive UTC datetime for compatibility with existing SQLite columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
