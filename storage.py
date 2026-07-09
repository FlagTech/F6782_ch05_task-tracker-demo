import json
import os
import tempfile
from pathlib import Path


DATA_FILE = Path(__file__).resolve().with_name("tasks.json")


class StorageError(Exception):
    """Raised when task data cannot be safely loaded or saved."""

    def __init__(self, path, message):
        self.path = Path(path)
        super().__init__(f"{message}: {self.path}")


def _validate_tasks(tasks, path):
    if not isinstance(tasks, list):
        raise StorageError(path, "Task data must contain a list of tasks")

    seen_ids = set()
    for index, task in enumerate(tasks):
        prefix = f"Task at index {index}"
        if not isinstance(task, dict):
            raise StorageError(path, f"{prefix} must be an object")

        task_id = task.get("id")
        if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id <= 0:
            raise StorageError(path, f"{prefix} has an invalid id")
        if task_id in seen_ids:
            raise StorageError(path, f"{prefix} has a duplicate id")
        seen_ids.add(task_id)

        title = task.get("title")
        if not isinstance(title, str) or not title.strip():
            raise StorageError(path, f"{prefix} has an invalid title")
        if not isinstance(task.get("completed"), bool):
            raise StorageError(path, f"{prefix} has an invalid completed value")

    return tasks


def _decode(data, path):
    # Bare lists were written by older versions and remain readable.
    if isinstance(data, list):
        tasks = data
    elif isinstance(data, dict) and "tasks" in data:
        tasks = data["tasks"]
    else:
        raise StorageError(path, "Task data must be an object with a 'tasks' field")
    return _validate_tasks(tasks, path)


def load_tasks():
    path = Path(DATA_FILE)
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            return _decode(json.load(file), path)
    except StorageError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StorageError(path, f"Could not load task data ({exc})") from exc


def save_tasks(tasks):
    path = Path(DATA_FILE)
    _validate_tasks(tasks, path)

    # Refuse to replace unreadable data: the user must recover or move it first.
    if path.exists():
        load_tasks()

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temp_path = Path(file.name)
            json.dump({"tasks": tasks}, file, indent=2)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())

        os.replace(temp_path, path)
        temp_path = None
    except (OSError, TypeError, ValueError) as exc:
        raise StorageError(path, f"Could not save task data ({exc})") from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
