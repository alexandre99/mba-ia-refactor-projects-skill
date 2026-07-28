from services.user_service import UserService

service = UserService()


def list_users():
    return service.list_users()


def get_user(user_id):
    return service.get_user(user_id)


def create_user(data):
    return service.create_user(data)


def update_user(user_id, data):
    return service.update_user(user_id, data)


def delete_user(user_id):
    return service.delete_user(user_id)


def user_tasks(user_id):
    return service.user_tasks(user_id)


def login(data):
    return service.login(data)
