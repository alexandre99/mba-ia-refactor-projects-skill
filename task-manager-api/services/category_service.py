from models.category import Category
from repositories.unit_of_work import UnitOfWork
from services.transaction import commit_or_error
from utils.errors import ApplicationError, NotFoundError


class CategoryService:
    def __init__(self, unit_of_work=None):
        self.unit_of_work = unit_of_work or UnitOfWork()

    def list_categories(self):
        result = []
        for category in self.unit_of_work.categories.list_with_tasks():
            result.append({**category.to_dict(), "task_count": len(category.tasks)})
        return result

    def create_category(self, data):
        if not isinstance(data, dict) or not data:
            raise ApplicationError("Dados inválidos", 400)
        name = data.get("name")
        if not name:
            raise ApplicationError("Nome é obrigatório")
        category = Category(
            name=name,
            description=data.get("description", ""),
            color=data.get("color", "#000000"),
        )
        self.unit_of_work.categories.add(category)
        commit_or_error(self.unit_of_work, "Erro ao criar categoria")
        return category.to_dict()

    def update_category(self, category_id, data):
        category = self.unit_of_work.categories.get(category_id)
        if not category:
            raise NotFoundError("Categoria não encontrada")
        if not isinstance(data, dict):
            raise ApplicationError("Dados inválidos", 400)
        for field in ("name", "description", "color"):
            if field in data:
                setattr(category, field, data[field])
        commit_or_error(self.unit_of_work, "Erro ao atualizar")
        return category.to_dict()

    def delete_category(self, category_id):
        category = self.unit_of_work.categories.get(category_id)
        if not category:
            raise NotFoundError("Categoria não encontrada")
        self.unit_of_work.categories.delete(category)
        commit_or_error(self.unit_of_work, "Erro ao deletar")
        return {"message": "Categoria deletada"}
