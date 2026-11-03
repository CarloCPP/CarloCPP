import os
import shutil
import tempfile
import unittest
from datetime import datetime, timezone, timedelta

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import generate_night_shift as gen

class TestNightShiftGenerator(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.readme_path = os.path.join(self.test_dir, "README.md")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_normal_replacement(self):
        content = "BEFORE\n<!-- NIGHT_SHIFT_START -->\nOLD\n<!-- NIGHT_SHIFT_END -->\nAFTER"
        with open(self.readme_path, "w", encoding="utf-8") as f:
            f.write(content)

        stream = gen.generate_log_stream()
        gen.update_readme(self.readme_path, stream)

        with open(self.readme_path, "r", encoding="utf-8") as f:
            updated = f.read()

        self.assertTrue(updated.startswith("BEFORE\n<!-- NIGHT_SHIFT_START -->\n```text\n"))
        self.assertTrue(updated.endswith("\n```\n<!-- NIGHT_SHIFT_END -->\nAFTER"))
        self.assertIn("[THE NIGHT SHIFT / SYNTHETIC LOG]", updated)

    def test_fail_closed_missing_start(self):
        content = "BEFORE\nOLD\n<!-- NIGHT_SHIFT_END -->\nAFTER"
        with open(self.readme_path, "w", encoding="utf-8") as f:
            f.write(content)

        with self.assertRaises(ValueError):
            gen.update_readme(self.readme_path, "STREAM")

        # Verify file is unmodified
        with open(self.readme_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content)

    def test_fail_closed_missing_end(self):
        content = "BEFORE\n<!-- NIGHT_SHIFT_START -->\nOLD\nAFTER"
        with open(self.readme_path, "w", encoding="utf-8") as f:
            f.write(content)

        with self.assertRaises(ValueError):
            gen.update_readme(self.readme_path, "STREAM")

        with open(self.readme_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content)

    def test_fail_closed_inverted_markers(self):
        content = "BEFORE\n<!-- NIGHT_SHIFT_END -->\nOLD\n<!-- NIGHT_SHIFT_START -->\nAFTER"
        with open(self.readme_path, "w", encoding="utf-8") as f:
            f.write(content)

        with self.assertRaises(ValueError):
            gen.update_readme(self.readme_path, "STREAM")

        with open(self.readme_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content)

    def test_event_timestamps_strictly_in_past(self):
        HKT = timezone(timedelta(hours=8))
        ref_time = datetime(2026, 11, 3, 14, 0, 0, tzinfo=HKT)
        stream = gen.generate_log_stream(reference_time=ref_time)
        self.assertIn("Generated: 2026-11-03 14:00 HKT", stream)

if __name__ == "__main__":
    unittest.main()
