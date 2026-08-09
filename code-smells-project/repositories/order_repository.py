from database import get_db


def create_order(usuario_id, items, total):
    db = get_db()
    with db:
        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, "pendente", total),
        )
        pedido_id = cursor.lastrowid

        for item in items:
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
            )
            db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

    return {"pedido_id": pedido_id, "total": total}


def _orders_for_query(query, params):
    cursor = get_db().execute(query, params)
    orders = {}
    for row in cursor.fetchall():
        order = orders.setdefault(
            row["pedido_id"],
            {
                "id": row["pedido_id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            },
        )
        if row["item_id"] is not None:
            order["itens"].append(
                {
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"] or "Desconhecido",
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                }
            )
    return list(orders.values())


_ORDER_QUERY = """
    SELECT
        p.id AS pedido_id,
        p.usuario_id,
        p.status,
        p.total,
        p.criado_em,
        i.id AS item_id,
        i.produto_id,
        i.quantidade,
        i.preco_unitario,
        pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
    {where_clause}
    ORDER BY p.id, i.id
"""


def list_orders():
    return _orders_for_query(_ORDER_QUERY.format(where_clause=""), ())


def list_orders_for_user(user_id):
    return _orders_for_query(
        _ORDER_QUERY.format(where_clause="WHERE p.usuario_id = ?"), (user_id,)
    )


def update_order_status(order_id, status):
    db = get_db()
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, order_id))
    db.commit()


def sales_summary():
    cursor = get_db().execute(
        """
        SELECT
            COUNT(*) AS total_pedidos,
            COALESCE(SUM(total), 0) AS faturamento_bruto,
            SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END) AS pedidos_pendentes,
            SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END) AS pedidos_aprovados,
            SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END) AS pedidos_cancelados
        FROM pedidos
        """
    )
    row = cursor.fetchone()
    return {
        "total_pedidos": row["total_pedidos"],
        "faturamento_bruto": row["faturamento_bruto"],
        "pedidos_pendentes": row["pedidos_pendentes"] or 0,
        "pedidos_aprovados": row["pedidos_aprovados"] or 0,
        "pedidos_cancelados": row["pedidos_cancelados"] or 0,
    }
