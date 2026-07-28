from services.category_service import CategoryService

service = CategoryService()


def list_categories():
    return service.list_categories()


def create_category(data):
    return service.create_category(data)


def update_category(category_id, data):
    return service.update_category(category_id, data)


def delete_category(category_id):
    return service.delete_category(category_id)
