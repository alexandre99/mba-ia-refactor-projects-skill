from domain import parse_product_payload, parse_search_filters
from repositories import product_repository


def list_products():
    return product_repository.list_products()


def get_product(product_id):
    return product_repository.get_product(product_id)


def create_product(data):
    values = parse_product_payload(data, strict=True)
    return product_repository.create_product(**values)


def update_product(product_id, data):
    if product_repository.get_product(product_id) is None:
        return False
    values = parse_product_payload(data, strict=True)
    product_repository.update_product(product_id, **values)
    return True


def delete_product(product_id):
    if product_repository.get_product(product_id) is None:
        return False
    product_repository.delete_product(product_id)
    return True


def search_products(args):
    filters = parse_search_filters(args)
    return product_repository.search_products(**filters)
