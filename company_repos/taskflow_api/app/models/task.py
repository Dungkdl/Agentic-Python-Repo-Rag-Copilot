"""Task model helpers for TaskFlow."""


class Task:
    """Simple task record with status transition helpers."""

    VALID_STATUSES = {"open", "in_progress", "blocked", "done"}

    def __init__(self, task_id: int, title: str, assignee: str, status: str = "open") -> None:
        """Create a task record."""
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid task status: {status}")

        self.task_id = task_id
        self.title = title
        self.assignee = assignee
        self.status = status

    def assign_to(self, assignee: str) -> None:
        """Change the task assignee."""
        self.assignee = assignee

    def mark_done(self) -> None:
        """Mark the task as done."""
        self.status = "done"

    def is_blocked(self) -> bool:
        """Return True when the task is blocked."""
        return self.status == "blocked"

    def to_dict(self) -> dict:
        """Serialize the task record."""
        return {
            "id": self.task_id,
            "title": self.title,
            "assignee": self.assignee,
            "status": self.status,
        }
