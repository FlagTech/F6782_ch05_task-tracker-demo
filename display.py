def print_menu():
    print()
    print("Task Tracker")
    print("1. Add task")
    print("2. List tasks")
    print("3. Complete task")
    print("4. Show stats")
    print("5. Save and exit")
    print("6. Exit without saving")
    print()


def print_tasks(tasks):
    if not tasks:
        print("No tasks yet.")
        return

    for task in tasks:
        status = "done" if task["completed"] else "open"
        print(f"#{task['id']} [{status}] {task['title']}")


def print_stats(stats):
    print(f"Total: {stats['total']}")
    print(f"Open: {stats['open']}")
    print(f"Completed: {stats['completed']}")
