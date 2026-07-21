"""Compatibility facade for callers that imported the legacy models module."""

from werkzeug.security import generate_password_hash

from repositories import user_repository
from services import order_service, product_service, user_service


def get_todos_produtos():
    return product_service.list_products()


def get_produto_por_id(id):
    return product_service.get_product(id)


def criar_produto(nome, descricao, preco, estoque, categoria):
    return product_service.create_product(
        {
            "nome": nome,
            "descricao": descricao,
            "preco": preco,
            "estoque": estoque,
            "categoria": categoria,
        }
    )


def atualizar_produto(id, nome, descricao, preco, estoque, categoria):
    return product_service.update_product(
        id,
        {
            "nome": nome,
            "descricao": descricao,
            "preco": preco,
            "estoque": estoque,
            "categoria": categoria,
        },
    )


def deletar_produto(id):
    return product_service.delete_product(id)


def get_todos_usuarios():
    return user_service.list_users()


def get_usuario_por_id(id):
    return user_service.get_user(id)


def login_usuario(email, senha):
    return user_service.authenticate(email, senha)


def criar_usuario(nome, email, senha, tipo="cliente"):
    return user_repository.create_user(nome, email, generate_password_hash(senha), tipo)


def criar_pedido(usuario_id, itens):
    return order_service.create_order(usuario_id, itens)


def get_pedidos_usuario(usuario_id):
    return order_service.list_orders_for_user(usuario_id)


def get_todos_pedidos():
    return order_service.list_orders()


def relatorio_vendas():
    return order_service.sales_report()


def atualizar_status_pedido(pedido_id, novo_status):
    order_service.update_order_status(pedido_id, novo_status)
    return True


def buscar_produtos(termo, categoria=None, preco_min=None, preco_max=None):
    class SearchArgs:
        def get(self, name, default=None):
            return {
                "q": termo,
                "categoria": categoria,
                "preco_min": preco_min,
                "preco_max": preco_max,
            }.get(name, default)

    return product_service.search_products(SearchArgs())
