from sqlalchemy.orm import selectinload

from database import db
from models.category import Category


class CategoryRepository:
    def list_with_tasks(self):
        return Category.query.options(selectinload(Category.tasks)).all()

    def get(self, category_id):
        return db.session.get(Category, category_id)

    def add(self, category):
        db.session.add(category)

    def delete(self, category):
        db.session.delete(category)
