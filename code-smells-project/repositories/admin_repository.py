from database import get_db


def reset_database():
    db = get_db()
    with db:
        db.execute("DELETE FROM itens_pedido")
        db.execute("DELETE FROM pedidos")
        db.execute("DELETE FROM produtos")
        db.execute("DELETE FROM usuarios")


def count_products():
    cursor = get_db().execute("SELECT COUNT(*) AS total FROM produtos")
    return [dict(row) for row in cursor.fetchall()]
