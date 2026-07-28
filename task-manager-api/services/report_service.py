from datetime import timedelta

from repositories.unit_of_work import UnitOfWork
from utils.errors import NotFoundError
from utils.time import utcnow


class ReportService:
    def __init__(self, unit_of_work=None):
        self.unit_of_work = unit_of_work or UnitOfWork()

    def summary(self):
        tasks = self.unit_of_work.tasks.list_with_relations()
        users = self.unit_of_work.users.list_with_tasks()
        categories = self.unit_of_work.categories.list_with_tasks()
        now = utcnow()
        seven_days_ago = now - timedelta(days=7)

        status_counts = {status: 0 for status in ("pending", "in_progress", "done", "cancelled")}
        priority_counts = {priority: 0 for priority in range(1, 6)}
        overdue_tasks = []
        recent_tasks = 0
        recent_done = 0
        for task in tasks:
            status_counts[task.status] = status_counts.get(task.status, 0) + 1
            priority_counts[task.priority] = priority_counts.get(task.priority, 0) + 1
            if task.is_overdue():
                overdue_tasks.append(
                    {
                        "id": task.id,
                        "title": task.title,
                        "due_date": str(task.due_date),
                        "days_overdue": (now - task.due_date).days,
                    }
                )
            if task.created_at and task.created_at >= seven_days_ago:
                recent_tasks += 1
            if task.status == "done" and task.updated_at and task.updated_at >= seven_days_ago:
                recent_done += 1

        user_stats = []
        for user in users:
            user_tasks = list(user.tasks)
            completed = sum(task.status == "done" for task in user_tasks)
            total = len(user_tasks)
            user_stats.append(
                {
                    "user_id": user.id,
                    "user_name": user.name,
                    "total_tasks": total,
                    "completed_tasks": completed,
                    "completion_rate": round((completed / total) * 100, 2) if total else 0,
                }
            )

        return {
            "generated_at": str(now),
            "overview": {
                "total_tasks": len(tasks),
                "total_users": len(users),
                "total_categories": len(categories),
            },
            "tasks_by_status": status_counts,
            "tasks_by_priority": {
                "critical": priority_counts[1],
                "high": priority_counts[2],
                "medium": priority_counts[3],
                "low": priority_counts[4],
                "minimal": priority_counts[5],
            },
            "overdue": {"count": len(overdue_tasks), "tasks": overdue_tasks},
            "recent_activity": {
                "tasks_created_last_7_days": recent_tasks,
                "tasks_completed_last_7_days": recent_done,
            },
            "user_productivity": user_stats,
        }

    def user_report(self, user_id):
        user = self.unit_of_work.users.get(user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        tasks = self.unit_of_work.tasks.for_user(user_id)
        counts = {status: 0 for status in ("done", "pending", "in_progress", "cancelled")}
        overdue = 0
        high_priority = 0
        for task in tasks:
            counts[task.status] = counts.get(task.status, 0) + 1
            high_priority += task.priority <= 2
            overdue += task.is_overdue()
        total = len(tasks)
        return {
            "user": {"id": user.id, "name": user.name, "email": user.email},
            "statistics": {
                "total_tasks": total,
                "done": counts["done"],
                "pending": counts["pending"],
                "in_progress": counts["in_progress"],
                "cancelled": counts["cancelled"],
                "overdue": overdue,
                "high_priority": high_priority,
                "completion_rate": round((counts["done"] / total) * 100, 2) if total else 0,
            },
        }
