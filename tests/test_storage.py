import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import storage


VALID_TASK = {"id": 1, "title": "Buy milk", "completed": False}
DEFAULT_DATA_FILE = storage.DATA_FILE


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_file = Path(self.temp_dir.name) / "tasks.json"
        self.data_patch = patch.object(storage, "DATA_FILE", self.data_file)
        self.data_patch.start()
        self.addCleanup(self.data_patch.stop)

    def test_data_file_defaults_to_project_directory(self):
        self.assertEqual(
            DEFAULT_DATA_FILE,
            Path(storage.__file__).resolve().parent / "tasks.json",
        )

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(storage.load_tasks(), [])

    def test_save_uses_canonical_shape_and_round_trips_extra_fields(self):
        tasks = [{**VALID_TASK, "priority": "high"}]
        storage.save_tasks(tasks)

        self.assertEqual(json.loads(self.data_file.read_text(encoding="utf-8")), {"tasks": tasks})
        self.assertEqual(storage.load_tasks(), tasks)

    def test_load_supports_legacy_bare_list(self):
        self.data_file.write_text(json.dumps([VALID_TASK]), encoding="utf-8")
        self.assertEqual(storage.load_tasks(), [VALID_TASK])

    def test_invalid_json_and_blank_file_include_path(self):
        for contents in ("", "{"):
            with self.subTest(contents=contents):
                self.data_file.write_text(contents, encoding="utf-8")
                with self.assertRaises(storage.StorageError) as caught:
                    storage.load_tasks()
                self.assertIn(str(self.data_file), str(caught.exception))

    def test_rejects_invalid_roots(self):
        invalid = ({}, {"tasks": {}}, "tasks", 1, None)
        for value in invalid:
            with self.subTest(value=value):
                self.data_file.write_text(json.dumps(value), encoding="utf-8")
                with self.assertRaises(storage.StorageError):
                    storage.load_tasks()

    def test_rejects_invalid_task_fields(self):
        invalid_tasks = [
            ["not an object"],
            [{"id": True, "title": "x", "completed": False}],
            [{"id": 0, "title": "x", "completed": False}],
            [{"id": 1, "title": "   ", "completed": False}],
            [{"id": 1, "title": "x", "completed": 1}],
            [VALID_TASK, {"id": 1, "title": "duplicate", "completed": True}],
        ]
        for tasks in invalid_tasks:
            with self.subTest(tasks=tasks):
                self.data_file.write_text(json.dumps({"tasks": tasks}), encoding="utf-8")
                with self.assertRaises(storage.StorageError):
                    storage.load_tasks()

    def test_save_rejects_invalid_tasks_without_creating_file(self):
        with self.assertRaises(storage.StorageError):
            storage.save_tasks([{"id": 1, "title": "", "completed": False}])
        self.assertFalse(self.data_file.exists())

    def test_save_does_not_overwrite_corrupt_existing_file(self):
        original = "not json"
        self.data_file.write_text(original, encoding="utf-8")
        with self.assertRaises(storage.StorageError):
            storage.save_tasks([VALID_TASK])
        self.assertEqual(self.data_file.read_text(encoding="utf-8"), original)

    def test_replace_failure_preserves_original_and_removes_temp_file(self):
        original = json.dumps({"tasks": [VALID_TASK]})
        self.data_file.write_text(original, encoding="utf-8")
        new_tasks = [{"id": 2, "title": "New", "completed": False}]

        with patch("storage.os.replace", side_effect=OSError("disk failure")):
            with self.assertRaises(storage.StorageError):
                storage.save_tasks(new_tasks)

        self.assertEqual(self.data_file.read_text(encoding="utf-8"), original)
        self.assertEqual(list(self.data_file.parent.glob(f".{self.data_file.name}.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
