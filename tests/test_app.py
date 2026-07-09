import io
import unittest
from unittest.mock import patch

import app
import storage


class AppTests(unittest.TestCase):
    def run_app(self, inputs, tasks=None):
        output = io.StringIO()
        with patch.object(storage, "load_tasks", return_value=[] if tasks is None else tasks), \
             patch("builtins.input", side_effect=inputs), \
             patch("sys.stdout", output):
            app.main()
        return output.getvalue()

    def test_complete_reports_all_three_results(self):
        tasks = [{"id": 7, "title": "Seven", "completed": False}]
        output = self.run_app(["3", "7", "3", "7", "3", "8", "6", "y"], tasks)
        self.assertIn("Task #7 completed.", output)
        self.assertIn("Task #7 is already completed.", output)
        self.assertIn("Task #8 was not found.", output)

    def test_invalid_inputs_and_cancelled_discard(self):
        output = self.run_app(["1", "   ", "1", "Keep", "6", "n", "6", "yes"])
        self.assertIn("Task title cannot be empty", output)
        self.assertIn("Exit cancelled.", output)

    def test_save_error_stays_in_loop_and_does_not_claim_success(self):
        error = storage.StorageError("tasks.json", "disk full")
        output = io.StringIO()
        with patch.object(storage, "load_tasks", return_value=[]), \
             patch.object(storage, "save_tasks", side_effect=error), \
             patch("builtins.input", side_effect=["5", "6"]), \
             patch("sys.stdout", output):
            app.main()
        text = output.getvalue()
        self.assertIn("Could not save tasks", text)
        self.assertNotIn("Tasks saved", text)
        self.assertIn("Goodbye", text)

    def test_load_error_is_friendly(self):
        error = storage.StorageError("broken.json", "invalid JSON")
        output = io.StringIO()
        with patch.object(storage, "load_tasks", side_effect=error), patch("sys.stdout", output):
            app.main()
        self.assertIn("broken.json", output.getvalue())
        self.assertNotIn("Traceback", output.getvalue())

    def test_keyboard_interrupt_is_clean(self):
        output = self.run_app([KeyboardInterrupt()])
        self.assertIn("Input interrupted", output)


if __name__ == "__main__":
    unittest.main()
