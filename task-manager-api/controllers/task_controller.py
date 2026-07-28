from services.task_service import TaskService

service = TaskService()


def list_tasks():
    return service.list_tasks()


def get_task(task_id):
    return service.get_task(task_id)


def create_task(data):
    return service.create_task(data)


def update_task(task_id, data):
    return service.update_task(task_id, data)


def delete_task(task_id):
    return service.delete_task(task_id)


def search_tasks(query, status, priority, user_id):
    return service.search_tasks(query, status, priority, user_id)


def stats():
    return service.stats()
