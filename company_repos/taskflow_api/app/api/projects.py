"""API layer for project operations."""

from app.services.project_service import ProjectService


def create_project(name: str, owner: str) -> dict:
    """Create a project through the service layer."""
    service = ProjectService()
    return service.create_project(name=name, owner=owner)


def summarize_project(name: str, open_task_count: int) -> dict:
    """Return a project summary and notification digest."""
    service = ProjectService()
    return service.summarize_project(
        name=name,
        open_task_count=open_task_count,
    )
