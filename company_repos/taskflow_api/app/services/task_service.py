from app.models.task import Task
from app.services.notification_service import NotificationService


class TaskService:
    def __init__(self) -> None:
        self.notification_service = NotificationService()

    def list_tasks(self) -> list[dict]:
        return [
            {
                "id": 1,
                "title": "Review onboarding guide",
                "status": "open",
            }
        ]

    def create_task(self, title: str, assignee: str) -> dict:
        task = Task(task_id=2, title=title, assignee=assignee)
        notification = self.notification_service.build_assignment_message(
            title=title,
            assignee=assignee,
        )

        result = task.to_dict()
        result["notification"] = notification
        return result

    def complete_task(self, task_id: int, title: str, assignee: str) -> dict:
        task = Task(task_id=task_id, title=title, assignee=assignee)
        task.mark_done()
        return task.to_dict()
