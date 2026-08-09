import logging
import smtplib


class NotificationService:
    def __init__(self, config=None):
        config = config or {}
        self.notifications = []
        self.email_host = config.get("SMTP_HOST")
        self.email_port = config.get("SMTP_PORT", 587)
        self.email_user = config.get("SMTP_USER")
        self.email_password = config.get("SMTP_PASSWORD")
        self.logger = logging.getLogger(__name__)

    def send_email(self, to, subject, body):
        if not all((self.email_host, self.email_user, self.email_password)):
            self.logger.warning("SMTP notification skipped because it is not configured")
            return False
        try:
            with smtplib.SMTP(self.email_host, self.email_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                message = f"Subject: {subject}\n\n{body}"
                server.sendmail(self.email_user, to, message)
            self.logger.info("Email notification sent")
            return True
        except (OSError, smtplib.SMTPException):
            self.logger.exception("Email notification failed")
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        self.send_email(user.email, subject, body)
        self.notifications.append(
            {"type": "task_assigned", "user_id": user.id, "task_id": task.id}
        )

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [notification for notification in self.notifications if notification["user_id"] == user_id]
