from models.task import Task
from repositories.unit_of_work import UnitOfWork
from services.transaction import commit_or_error
from utils.errors import ApplicationError, NotFoundError
from utils.time import utcnow
from utils.validation import normalize_task_payload


class TaskService:
    def __init__(self, unit_of_work=None):
        self.unit_of_work = unit_of_work or UnitOfWork()

    @staticmethod
    def _serialize(task, include_relations=False):
        data = task.to_dict()
        if include_relations:
            data["overdue"] = task.is_overdue()
            data["user_name"] = task.user.name if task.user else None
            data["category_name"] = task.category.name if task.category else None
        return data

    def _validate_relations(self, values):
        if values.get("user_id") and not self.unit_of_work.users.get(values["user_id"]):
            raise NotFoundError("Usuário não encontrado")
        if values.get("category_id") and not self.unit_of_work.categories.get(values["category_id"]):
            raise NotFoundError("Categoria não encontrada")

    def list_tasks(self):
        return [self._serialize(task, include_relations=True) for task in self.unit_of_work.tasks.list_with_relations()]

    def get_task(self, task_id):
        task = self.unit_of_work.tasks.get(task_id)
        if not task:
            raise NotFoundError("Task não encontrada")
        return self._serialize(task, include_relations=False) | {"overdue": task.is_overdue()}

    def create_task(self, data):
        values = normalize_task_payload(data)
        self._validate_relations(values)
        task = Task(
            title=values["title"],
            description=values.get("description", ""),
            status=values["status"],
            priority=values["priority"],
            user_id=values.get("user_id"),
            category_id=values.get("category_id"),
            due_date=values.get("due_date"),
            tags=values.get("tags"),
        )
        self.unit_of_work.tasks.add(task)
        commit_or_error(self.unit_of_work, "Erro ao criar task")
        return task.to_dict()

    def update_task(self, task_id, data):
        task = self.unit_of_work.tasks.get(task_id)
        if not task:
            raise NotFoundError("Task não encontrada")
        values = normalize_task_payload(data, partial=True)
        self._validate_relations(values)
        for field, value in values.items():
            setattr(task, field, value)
        task.updated_at = utcnow()
        commit_or_error(self.unit_of_work, "Erro ao atualizar")
        return task.to_dict()

    def delete_task(self, task_id):
        task = self.unit_of_work.tasks.get(task_id)
        if not task:
            raise NotFoundError("Task não encontrada")
        self.unit_of_work.tasks.delete(task)
        commit_or_error(self.unit_of_work, "Erro ao deletar")
        return {"message": "Task deletada com sucesso"}

    def search_tasks(self, query_text="", status="", priority="", user_id=""):
        try:
            parsed_priority = int(priority) if priority else None
            parsed_user_id = int(user_id) if user_id else None
        except ValueError as exc:
            raise ApplicationError("Filtro inválido", 400) from exc
        return [
            self._serialize(task)
            for task in self.unit_of_work.tasks.search(query_text, status, parsed_priority, parsed_user_id)
        ]

    def stats(self):
        tasks = self.unit_of_work.tasks.list_with_relations()
        counts = {status: 0 for status in ("pending", "in_progress", "done", "cancelled")}
        overdue = 0
        for task in tasks:
            counts[task.status] = counts.get(task.status, 0) + 1
            if task.is_overdue():
                overdue += 1
        total = len(tasks)
        return {
            "total": total,
            **counts,
            "overdue": overdue,
            "completion_rate": round((counts["done"] / total) * 100, 2) if total else 0,
        }
