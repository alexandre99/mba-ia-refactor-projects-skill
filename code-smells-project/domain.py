PRODUCT_CATEGORIES = (
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
)

ORDER_STATUSES = (
    "pendente",
    "aprovado",
    "enviado",
    "entregue",
    "cancelado",
)


def parse_product_payload(data, strict=False):
    from errors import ValidationError

    if not isinstance(data, dict) or not data:
        raise ValidationError("Dados inválidos")

    for field, label in (("nome", "Nome"), ("preco", "Preço"), ("estoque", "Estoque")):
        if field not in data:
            raise ValidationError(f"{label} é obrigatório")

    nome = data["nome"]
    preco = data["preco"]
    estoque = data["estoque"]
    descricao = data.get("descricao", "")
    categoria = data.get("categoria", "geral")

    if not isinstance(nome, str):
        raise ValidationError("Nome inválido")
    if not isinstance(preco, (int, float)) or isinstance(preco, bool):
        raise ValidationError("Preço inválido")
    if not isinstance(estoque, int) or isinstance(estoque, bool):
        raise ValidationError("Estoque inválido")
    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")

    if strict:
        if len(nome) < 2:
            raise ValidationError("Nome muito curto")
        if len(nome) > 200:
            raise ValidationError("Nome muito longo")
        if categoria not in PRODUCT_CATEGORIES:
            raise ValidationError(
                "Categoria inválida. Válidas: " + str(list(PRODUCT_CATEGORIES))
            )

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def parse_search_filters(args):
    from errors import ValidationError

    def parse_price(name):
        value = args.get(name)
        if value in (None, ""):
            return None
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"{name} inválido") from exc

    return {
        "termo": args.get("q", ""),
        "categoria": args.get("categoria"),
        "preco_min": parse_price("preco_min"),
        "preco_max": parse_price("preco_max"),
    }
