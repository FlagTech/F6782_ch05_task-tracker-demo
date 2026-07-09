from enum import Enum


class CompleteTaskResult(str, Enum):
    COMPLETED = "completed"
    ALREADY_COMPLETED = "already_completed"
    NOT_FOUND = "not_found"


class TaskManager:
    def __init__(self, tasks=None):
        self.tasks = [] if tasks is None else tasks

    def add_task(self, title):
        if not isinstance(title, str):
            raise TypeError("Task title must be a string.")

        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty.")

        valid_ids = (
            task.get("id")
            for task in self.tasks
            if isinstance(task, dict)
            and isinstance(task.get("id"), int)
            and not isinstance(task.get("id"), bool)
            and task["id"] > 0
        )
        next_id = max(valid_ids, default=0) + 1
        task = {
            "id": next_id,
            "title": title,
            "completed": False,
        }
        self.tasks.append(task)
        return task

    def complete_task(self, task_id):
        task = next(
            (task for task in self.tasks if task.get("id") == task_id),
            None,
        )
        if task is None:
            return CompleteTaskResult.NOT_FOUND
        if task["completed"]:
            return CompleteTaskResult.ALREADY_COMPLETED

        task["completed"] = True
        return CompleteTaskResult.COMPLETED

    def get_stats(self):
        completed = sum(1 for task in self.tasks if task["completed"])
        return {
            "total": len(self.tasks),
            "open": len(self.tasks) - completed,
            "completed": completed,
        }
