from display import print_menu, print_tasks, print_stats
import storage
from task_manager import CompleteTaskResult, TaskManager


def main():
    try:
        manager = TaskManager(storage.load_tasks())
    except storage.StorageError as exc:
        print(f"Could not open task data at {exc.path}.")
        print(f"Details: {exc}")
        print("Move or repair that file, then try again.")
        return

    dirty = False

    while True:
        try:
            print_menu()
            choice = input("Choose an option (1-6): ").strip()

            if choice == "1":
                title = input("Task title: ")
                try:
                    task = manager.add_task(title)
                except (TypeError, ValueError) as exc:
                    print(f"Could not add task: {exc}")
                    continue
                dirty = True
                print(f"Added task #{task['id']}: {task['title']}")
            elif choice == "2":
                print_tasks(manager.tasks)
            elif choice == "3":
                raw_id = input("Task #ID to complete (positive integer): ").strip()
                if not raw_id.isdigit() or int(raw_id) <= 0:
                    print("Please enter a positive integer task #ID.")
                    continue
                result = manager.complete_task(int(raw_id))
                if result == CompleteTaskResult.COMPLETED:
                    dirty = True
                    print(f"Task #{raw_id} completed.")
                elif result == CompleteTaskResult.ALREADY_COMPLETED:
                    print(f"Task #{raw_id} is already completed.")
                else:
                    print(f"Task #{raw_id} was not found.")
            elif choice == "4":
                print_stats(manager.get_stats())
            elif choice == "5":
                try:
                    storage.save_tasks(manager.tasks)
                except storage.StorageError as exc:
                    print(f"Could not save tasks to {exc.path}.")
                    print(f"Details: {exc}")
                    print("Your changes are still in memory; fix the problem and try again.")
                    continue
                print("Tasks saved. Goodbye.")
                return
            elif choice == "6":
                if dirty:
                    confirm = input("Discard unsaved changes? (y/N): ").strip().lower()
                    if confirm not in {"y", "yes"}:
                        print("Exit cancelled.")
                        continue
                print("Goodbye.")
                return
            else:
                print("Unknown option. Please choose a number from 1 to 6.")
        except (EOFError, KeyboardInterrupt):
            print("\nInput interrupted. No unsaved changes were written; goodbye.")
            return


if __name__ == "__main__":
    main()
