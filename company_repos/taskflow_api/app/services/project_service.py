"""Business logic for TaskFlow projects."""

from app.services.notification_service import NotificationService


class ProjectService:
    """Manage project summaries and notifications."""

    def __init__(self) -> None:
        """Initialize the project service."""
        self.notification_service = NotificationService()

    def create_project(self, name: str, owner: str) -> dict:
        """Create a project summary."""
        return {
            "id": 101,
            "name": name,
            "owner": owner,
            "status": "active",
        }

    def summarize_project(self, name: str, open_task_count: int) -> dict:
        """Return a project summary with a digest notification."""
        digest = self.notification_service.build_project_digest(
            project_name=name,
            open_task_count=open_task_count,
        )

        return {
            "name": name,
            "open_task_count": open_task_count,
            "digest": digest,
        }
