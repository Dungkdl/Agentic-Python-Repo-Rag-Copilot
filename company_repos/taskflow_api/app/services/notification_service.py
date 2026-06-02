"""Notification helpers for TaskFlow."""


class NotificationService:
    """Build notification payloads for task and project events."""

    def build_assignment_message(self, title: str, assignee: str) -> dict:
        """Create a task assignment notification payload."""
        return {
            "channel": "task_assignment",
            "recipient": assignee,
            "message": f"You were assigned to {title}",
        }

    def build_project_digest(self, project_name: str, open_task_count: int) -> dict:
        """Create a project digest notification payload."""
        return {
            "channel": "project_digest",
            "project": project_name,
            "open_task_count": open_task_count,
        }
