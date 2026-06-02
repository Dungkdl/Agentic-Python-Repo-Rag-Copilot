# TaskFlow API

TaskFlow API is a Python backend service for managing tasks, projects, and user work items.

## Purpose

The project helps teams create, update, assign, and track tasks.

## Tech Stack

- Python
- FastAPI-style API structure
- Service layer architecture

## Main Modules

- `app/api/tasks.py` handles task-related API functions.
- `app/services/task_service.py` contains task business logic.
- `app/api/projects.py` exposes project operations.
- `app/services/project_service.py` builds project summaries and digest notifications.
- `app/models/task.py` defines the Task model and status helpers.

## Setup

Install dependencies and run the application from `app/main.py`.

## Onboarding Notes

New developers should start by reading:

1. `README.md`
2. `app/main.py`
3. `app/api/tasks.py`
4. `app/services/task_service.py`

## Operational Rules

- Task statuses must be one of `open`, `in_progress`, `blocked`, or `done`.
- Assignment notifications use the `task_assignment` channel.
- Project digests use the `project_digest` channel and include `open_task_count`.
