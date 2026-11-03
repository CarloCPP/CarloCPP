import os
import shutil
import tempfile
import unittest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import light_window as lw

class TestLightWindow(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.readme_path = os.path.join(self.test_dir, "README.md")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_sanitize_username(self):
        self.assertEqual(lw.sanitize_username("octocat"), "octocat")
        self.assertEqual(lw.sanitize_username("@octocat"), "octocat")
        self.assertEqual(lw.sanitize_username("user-123"), "user-123")
        with self.assertRaises(ValueError):
            lw.sanitize_username("invalid;rm -rf /")
        with self.assertRaises(ValueError):
            lw.sanitize_username("has spaces")

    def test_normal_light_window(self):
        content = "BEFORE\n<!-- CITY_LIGHTS_START -->\nOLD\n<!-- CITY_LIGHTS_END -->\nAFTER"
        with open(self.readme_path, "w", encoding="utf-8") as f:
            f.write(content)

        lw.update_readme(self.readme_path, "Alice")

        with open(self.readme_path, "r", encoding="utf-8") as f:
            updated = f.read()

        self.assertIn("🏮 Window #01 ── @CarloCPP (City Architect)", updated)
        self.assertIn("🏮 Window #02 ── @Alice", updated)
        self.assertTrue(updated.startswith("BEFORE\n<!-- CITY_LIGHTS_START -->\n```text\n"))
        self.assertTrue(updated.endswith("\n```\n<!-- CITY_LIGHTS_END -->\nAFTER"))

    def test_fail_closed_missing_markers(self):
        content = "NO MARKERS HERE"
        with open(self.readme_path, "w", encoding="utf-8") as f:
            f.write(content)

        with self.assertRaises(ValueError):
            lw.update_readme(self.readme_path, "Alice")

        with open(self.readme_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content)

if __name__ == "__main__":
    unittest.main()
