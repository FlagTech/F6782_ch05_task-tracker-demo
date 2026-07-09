import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app
import storage


class CliRestartTests(unittest.TestCase):
    def test_save_then_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            data_file = Path(directory) / "tasks.json"
            with patch.object(storage, "DATA_FILE", data_file):
                with patch("builtins.input", side_effect=["1", "Buy milk", "1", "Write report", "3", "2", "5"]), \
                     patch("sys.stdout", io.StringIO()):
                    app.main()

                output = io.StringIO()
                with patch("builtins.input", side_effect=["2", "4", "6"]), \
                     patch("sys.stdout", output):
                    app.main()

            text = output.getvalue()
            self.assertIn("#1 [open] Buy milk", text)
            self.assertIn("#2 [done] Write report", text)
            self.assertIn("Total: 2", text)
            self.assertIn("Open: 1", text)
            self.assertIn("Completed: 1", text)


if __name__ == "__main__":
    unittest.main()
