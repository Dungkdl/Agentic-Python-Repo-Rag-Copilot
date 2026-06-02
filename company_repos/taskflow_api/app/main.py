from app.api.projects import create_project
from app.api.tasks import list_tasks


def main():
    project = create_project(name="Onboarding", owner="ops")
    tasks = list_tasks()
    print(project)
    print(tasks)


if __name__ == "__main__":
    main()
