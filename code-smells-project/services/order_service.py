from domain import ORDER_STATUSES
from errors import ValidationError
from repositories import order_repository, product_repository, user_repository


def create_order(usuario_id, items):
    if not isinstance(usuario_id, int) or isinstance(usuario_id, bool) or usuario_id <= 0:
        raise ValidationError("Usuario ID é obrigatório")
    if not isinstance(items, list) or not items:
        raise ValidationError("Pedido deve ter pelo menos 1 item")
    if user_repository.get_user(usuario_id) is None:
        raise ValidationError(f"Usuário {usuario_id} não encontrado")

    requested = {}
    normalized_items = []
    for item in items:
        if not isinstance(item, dict):
            raise ValidationError("Item de pedido inválido")
        product_id = item.get("produto_id")
        quantity = item.get("quantidade")
        if (
            not isinstance(product_id, int)
            or isinstance(product_id, bool)
            or not isinstance(quantity, int)
            or isinstance(quantity, bool)
            or quantity <= 0
        ):
            raise ValidationError("Item de pedido inválido")
        requested[product_id] = requested.get(product_id, 0) + quantity
        normalized_items.append({"produto_id": product_id, "quantidade": quantity})

    products = product_repository.get_products_by_ids(requested)
    total = 0
    for product_id, quantity in requested.items():
        product = products.get(product_id)
        if product is None:
            raise ValidationError(f"Produto {product_id} não encontrado")
        if product["estoque"] < quantity:
            raise ValidationError(f"Estoque insuficiente para {product['nome']}")

    for item in normalized_items:
        product = products[item["produto_id"]]
        item["preco_unitario"] = product["preco"]
        total += product["preco"] * item["quantidade"]

    return order_repository.create_order(usuario_id, normalized_items, total)


def list_orders():
    return order_repository.list_orders()


def list_orders_for_user(user_id):
    return order_repository.list_orders_for_user(user_id)


def update_order_status(order_id, status):
    if status not in ORDER_STATUSES:
        raise ValidationError("Status inválido")
    order_repository.update_order_status(order_id, status)


def sales_report():
    summary = order_repository.sales_summary()
    gross = float(summary["faturamento_bruto"] or 0)
    if gross > 10000:
        discount = gross * 0.1
    elif gross > 5000:
        discount = gross * 0.05
    elif gross > 1000:
        discount = gross * 0.02
    else:
        discount = 0

    total_orders = summary["total_pedidos"]
    return {
        "total_pedidos": total_orders,
        "faturamento_bruto": round(gross, 2),
        "desconto_aplicavel": round(discount, 2),
        "faturamento_liquido": round(gross - discount, 2),
        "pedidos_pendentes": summary["pedidos_pendentes"],
        "pedidos_aprovados": summary["pedidos_aprovados"],
        "pedidos_cancelados": summary["pedidos_cancelados"],
        "ticket_medio": round(gross / total_orders, 2) if total_orders > 0 else 0,
    }
