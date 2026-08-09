from database import get_db


_PRODUCT_COLUMNS = "id, nome, descricao, preco, estoque, categoria, ativo, criado_em"


def _to_product(row):
    if row is None:
        return None
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def list_products():
    cursor = get_db().execute(f"SELECT {_PRODUCT_COLUMNS} FROM produtos")
    return [_to_product(row) for row in cursor.fetchall()]


def get_product(product_id):
    cursor = get_db().execute(
        f"SELECT {_PRODUCT_COLUMNS} FROM produtos WHERE id = ?", (product_id,)
    )
    return _to_product(cursor.fetchone())


def get_products_by_ids(product_ids):
    if not product_ids:
        return {}
    placeholders = ", ".join("?" for _ in product_ids)
    cursor = get_db().execute(
        f"SELECT {_PRODUCT_COLUMNS} FROM produtos WHERE id IN ({placeholders})",
        tuple(product_ids),
    )
    return {row["id"]: _to_product(row) for row in cursor.fetchall()}


def create_product(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def update_product(product_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, product_id),
    )
    db.commit()


def delete_product(product_id):
    db = get_db()
    db.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
    db.commit()


def search_products(termo, categoria=None, preco_min=None, preco_max=None):
    query = f"SELECT {_PRODUCT_COLUMNS} FROM produtos WHERE 1 = 1"
    params = []

    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        like_term = f"%{termo}%"
        params.extend((like_term, like_term))
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)

    cursor = get_db().execute(query, tuple(params))
    return [_to_product(row) for row in cursor.fetchall()]
