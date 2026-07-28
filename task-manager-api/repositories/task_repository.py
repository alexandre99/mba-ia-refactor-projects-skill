from sqlalchemy.orm import joinedload

from database import db
from models.task import Task


class TaskRepository:
    def list_with_relations(self):
        return Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()

    def get(self, task_id):
        return db.session.get(Task, task_id)

    def for_user(self, user_id):
        return Task.query.filter_by(user_id=user_id).all()

    def add(self, task):
        db.session.add(task)

    def delete(self, task):
        db.session.delete(task)

    def search(self, query_text="", status="", priority=None, user_id=None):
        query = Task.query
        if query_text:
            pattern = f"%{query_text}%"
            query = query.filter(db.or_(Task.title.like(pattern), Task.description.like(pattern)))
        if status:
            query = query.filter(Task.status == status)
        if priority is not None:
            query = query.filter(Task.priority == priority)
        if user_id is not None:
            query = query.filter(Task.user_id == user_id)
        return query.all()

