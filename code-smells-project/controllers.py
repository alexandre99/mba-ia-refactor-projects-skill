from flask import current_app, jsonify, request

from errors import ApplicationError, ValidationError
from services import admin_service, health_service, order_service, product_service, user_service


def _run(operation, success_status=200):
    try:
        return jsonify(operation()), success_status
    except ApplicationError as error:
        return jsonify(error.payload), error.status_code


def listar_produtos():
    return _run(lambda: {"dados": product_service.list_products(), "sucesso": True})


def buscar_produto(id):
    def operation():
        produto = product_service.get_product(id)
        if produto is None:
            raise ApplicationError(
                "Produto não encontrado",
                status_code=404,
                payload={"erro": "Produto não encontrado", "sucesso": False},
            )
        return {"dados": produto, "sucesso": True}

    return _run(operation)


def criar_produto():
    return _run(
        lambda: {
            "dados": {"id": product_service.create_product(request.get_json(silent=True))},
            "sucesso": True,
            "mensagem": "Produto criado",
        },
        success_status=201,
    )


def atualizar_produto(id):
    def operation():
        if not product_service.update_product(id, request.get_json(silent=True)):
            raise ApplicationError("Produto não encontrado", status_code=404)
        return {"sucesso": True, "mensagem": "Produto atualizado"}

    return _run(operation)


def deletar_produto(id):
    def operation():
        if not product_service.delete_product(id):
            raise ApplicationError("Produto não encontrado", status_code=404)
        return {"sucesso": True, "mensagem": "Produto deletado"}

    return _run(operation)


def buscar_produtos():
    def operation():
        resultados = product_service.search_products(request.args)
        return {"dados": resultados, "total": len(resultados), "sucesso": True}

    return _run(operation)


def listar_usuarios():
    return _run(lambda: {"dados": user_service.list_users(), "sucesso": True})


def buscar_usuario(id):
    def operation():
        usuario = user_service.get_user(id)
        if usuario is None:
            raise ApplicationError("Usuário não encontrado", status_code=404)
        return {"dados": usuario, "sucesso": True}

    return _run(operation)


def criar_usuario():
    return _run(
        lambda: {
            "dados": {"id": user_service.create_user(request.get_json(silent=True))},
            "sucesso": True,
        },
        success_status=201,
    )


def login():
    def operation():
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict):
            raise ValidationError("Email e senha são obrigatórios")
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not email or not senha:
            raise ValidationError("Email e senha são obrigatórios")

        usuario = user_service.authenticate(email, senha)
        if usuario is None:
            raise ApplicationError(
                "Email ou senha inválidos",
                status_code=401,
                payload={"erro": "Email ou senha inválidos", "sucesso": False},
            )
        return {"dados": usuario, "sucesso": True, "mensagem": "Login OK"}

    return _run(operation)


def criar_pedido():
    def operation():
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict):
            raise ValidationError("Dados inválidos")
        return {
            "dados": order_service.create_order(dados.get("usuario_id"), dados.get("itens", [])),
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso",
        }

    return _run(operation, success_status=201)


def listar_pedidos_usuario(usuario_id):
    return _run(
        lambda: {"dados": order_service.list_orders_for_user(usuario_id), "sucesso": True}
    )


def listar_todos_pedidos():
    return _run(lambda: {"dados": order_service.list_orders(), "sucesso": True})


def atualizar_status_pedido(pedido_id):
    def operation():
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict):
            raise ValidationError("Dados inválidos")
        order_service.update_order_status(pedido_id, dados.get("status", ""))
        return {"sucesso": True, "mensagem": "Status atualizado"}

    return _run(operation)


def relatorio_vendas():
    return _run(lambda: {"dados": order_service.sales_report(), "sucesso": True})


def health_check():
    return _run(lambda: health_service.get_health(current_app.config["APP_ENV"]))


def reset_database():
    def operation():
        admin_service.reset_database(
            request.headers.get("X-Admin-Token"), current_app.config["ADMIN_TOKEN"]
        )
        return {"mensagem": "Banco de dados resetado", "sucesso": True}

    return _run(operation)


def executar_query():
    def operation():
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict):
            raise ValidationError("Dados inválidos")
        rows = admin_service.execute_query(dados.get("sql", ""))
        return {"dados": rows, "sucesso": True}

    return _run(operation)
