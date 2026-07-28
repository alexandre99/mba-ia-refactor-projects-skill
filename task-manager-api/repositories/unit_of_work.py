from database import db
from repositories.category_repository import CategoryRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository


class UnitOfWork:
    def __init__(self):
        self.users = UserRepository()
        self.tasks = TaskRepository()
        self.categories = CategoryRepository()

    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()
