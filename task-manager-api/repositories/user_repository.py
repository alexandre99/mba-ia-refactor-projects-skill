from sqlalchemy.orm import selectinload

from database import db
from models.user import User


class UserRepository:
    def list_with_tasks(self):
        return User.query.options(selectinload(User.tasks)).all()

    def get(self, user_id):
        return db.session.get(User, user_id)

    def find_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def add(self, user):
        db.session.add(user)

    def delete(self, user):
        db.session.delete(user)
