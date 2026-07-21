from database import get_db


def get_health_counts():
    db = get_db()
    db.execute("SELECT 1").fetchone()
    counts = {}
    for table in ("produtos", "usuarios", "pedidos"):
        row = db.execute(f"SELECT COUNT(*) AS total FROM {table}").fetchone()
        counts[table] = row["total"]
    return counts
