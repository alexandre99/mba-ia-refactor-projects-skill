from auth import create_access_token
from models.user import User
from repositories.unit_of_work import UnitOfWork
from services.transaction import commit_or_error
from utils.errors import (
    ApplicationError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
)
from utils.validation import validate_user_payload


class UserService:
    def __init__(self, unit_of_work=None):
        self.unit_of_work = unit_of_work or UnitOfWork()

    def list_users(self):
        return [
            {
                **user.to_dict(),
                "task_count": len(user.tasks),
            }
            for user in self.unit_of_work.users.list_with_tasks()
        ]

    def get_user(self, user_id):
        user = self.unit_of_work.users.get(user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        tasks = self.unit_of_work.tasks.for_user(user_id)
        return {**user.to_dict(), "tasks": [task.to_dict() for task in tasks]}

    def create_user(self, data):
        values = validate_user_payload(data)
        if self.unit_of_work.users.find_by_email(values["email"]):
            raise ConflictError("Email já cadastrado")
        user = User(
            name=values["name"],
            email=values["email"],
            role=values.get("role", "user"),
        )
        user.set_password(values["password"])
        self.unit_of_work.users.add(user)
        commit_or_error(self.unit_of_work, "Erro ao criar usuário")
        return user.to_dict()

    def update_user(self, user_id, data):
        user = self.unit_of_work.users.get(user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        values = validate_user_payload(data, partial=True)
        if "email" in values:
            existing = self.unit_of_work.users.find_by_email(values["email"])
            if existing and existing.id != user_id:
                raise ConflictError("Email já cadastrado")
        for field in ("name", "email", "role", "active"):
            if field in values:
                setattr(user, field, values[field])
        if "password" in values:
            user.set_password(values["password"])
        commit_or_error(self.unit_of_work, "Erro ao atualizar")
        return user.to_dict()

    def delete_user(self, user_id):
        user = self.unit_of_work.users.get(user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        for task in self.unit_of_work.tasks.for_user(user_id):
            self.unit_of_work.tasks.delete(task)
        self.unit_of_work.users.delete(user)
        commit_or_error(self.unit_of_work, "Erro ao deletar")
        return {"message": "Usuário deletado com sucesso"}

    def user_tasks(self, user_id):
        if not self.unit_of_work.users.get(user_id):
            raise NotFoundError("Usuário não encontrado")
        result = []
        for task in self.unit_of_work.tasks.for_user(user_id):
            result.append(
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "created_at": str(task.created_at),
                    "due_date": str(task.due_date) if task.due_date else None,
                    "overdue": task.is_overdue(),
                }
            )
        return result

    def login(self, data):
        if not isinstance(data, dict) or not data:
            raise ApplicationError("Dados inválidos", 400)
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            raise ApplicationError("Email e senha são obrigatórios", 400)
        user = self.unit_of_work.users.find_by_email(email)
        if not user or not user.check_password(password):
            raise AuthenticationError()
        if not user.active:
            raise ApplicationError("Usuário inativo", 403)
        return {
            "message": "Login realizado com sucesso",
            "user": user.to_dict(),
            "token": create_access_token(user),
        }
