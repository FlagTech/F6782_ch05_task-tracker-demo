import unittest

from task_manager import CompleteTaskResult, TaskManager


class TaskManagerTests(unittest.TestCase):
    def test_none_creates_new_task_list(self):
        first = TaskManager()
        second = TaskManager()

        first.add_task("First")

        self.assertEqual(second.tasks, [])

    def test_passed_empty_list_is_used_directly(self):
        tasks = []

        manager = TaskManager(tasks)

        self.assertIs(manager.tasks, tasks)

    def test_add_task_trims_title(self):
        manager = TaskManager()

        task = manager.add_task("  Write tests  ")

        self.assertEqual(task["title"], "Write tests")

    def test_add_task_rejects_empty_title(self):
        manager = TaskManager()

        for title in ("", "   ", "\t\n"):
            with self.subTest(title=title):
                with self.assertRaises(ValueError):
                    manager.add_task(title)
        self.assertEqual(manager.tasks, [])

    def test_add_task_rejects_non_string_title(self):
        manager = TaskManager()

        for title in (None, 123, []):
            with self.subTest(title=title):
                with self.assertRaises(TypeError):
                    manager.add_task(title)
        self.assertEqual(manager.tasks, [])

    def test_add_task_uses_largest_positive_integer_id(self):
        manager = TaskManager([
            {"id": 10, "title": "Ten", "completed": False},
            {"id": 2, "title": "Two", "completed": False},
        ])

        task = manager.add_task("Next")

        self.assertEqual(task["id"], 11)

    def test_add_task_ignores_invalid_ids_and_avoids_collision(self):
        manager = TaskManager([
            {"id": 1, "title": "One", "completed": False},
            {"id": 3, "title": "Three", "completed": False},
            {"id": "99", "title": "Text id", "completed": False},
            {"id": -4, "title": "Negative id", "completed": False},
            {"id": True, "title": "Boolean id", "completed": False},
        ])

        task = manager.add_task("Next")

        self.assertEqual(task["id"], 4)

    def test_complete_task_uses_task_id_not_list_position(self):
        manager = TaskManager([
            {"id": 10, "title": "Old task", "completed": False},
            {"id": 20, "title": "New task", "completed": False},
        ])

        result = manager.complete_task(20)

        self.assertEqual(result, CompleteTaskResult.COMPLETED)
        self.assertFalse(manager.tasks[0]["completed"])
        self.assertTrue(manager.tasks[1]["completed"])

    def test_complete_task_reports_already_completed(self):
        manager = TaskManager([
            {"id": 7, "title": "Done", "completed": True},
        ])

        result = manager.complete_task(7)

        self.assertEqual(result, CompleteTaskResult.ALREADY_COMPLETED)
        self.assertTrue(manager.tasks[0]["completed"])

    def test_complete_task_reports_not_found_without_modifying_tasks(self):
        tasks = [{"id": 7, "title": "Open", "completed": False}]
        manager = TaskManager(tasks)
        before = [task.copy() for task in tasks]

        result = manager.complete_task(99)

        self.assertEqual(result, CompleteTaskResult.NOT_FOUND)
        self.assertEqual(manager.tasks, before)

    def test_stats_for_empty_list(self):
        self.assertEqual(TaskManager().get_stats(), {
            "total": 0, "open": 0, "completed": 0,
        })

    def test_stats_for_all_open_tasks(self):
        manager = TaskManager([
            {"id": 1, "title": "One", "completed": False},
            {"id": 2, "title": "Two", "completed": False},
        ])

        self.assertEqual(manager.get_stats(), {
            "total": 2, "open": 2, "completed": 0,
        })

    def test_stats_for_all_completed_tasks(self):
        manager = TaskManager([
            {"id": 1, "title": "One", "completed": True},
            {"id": 2, "title": "Two", "completed": True},
        ])

        self.assertEqual(manager.get_stats(), {
            "total": 2, "open": 0, "completed": 2,
        })

    def test_stats_for_two_open_and_one_completed(self):
        manager = TaskManager([
            {"id": 1, "title": "One", "completed": False},
            {"id": 2, "title": "Two", "completed": True},
            {"id": 3, "title": "Three", "completed": False},
        ])

        self.assertEqual(manager.get_stats(), {
            "total": 3, "open": 2, "completed": 1,
        })


if __name__ == "__main__":
    unittest.main()
