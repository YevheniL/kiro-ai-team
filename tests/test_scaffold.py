"""Tests for project_scaffold module."""

import os
import shutil
import tempfile
import unittest

from project_scaffold import slugify, create_project_structure, create_project_folder


class TestSlugify(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(slugify("Create a weather app"), "weather-app")

    def test_strips_greetings_and_filler(self):
        self.assertEqual(
            slugify("Hi, please create a tetris game on python"),
            "tetris-game-python",
        )

    def test_strips_special_chars(self):
        self.assertEqual(slugify("Fix bug #123!"), "fix-bug-123")

    def test_limits_to_four_words(self):
        self.assertEqual(
            slugify("implement the new login screen feature"),
            "new-login-screen-feature",
        )

    def test_empty_string(self):
        self.assertEqual(slugify(""), "project")

    def test_only_filler_words(self):
        self.assertEqual(slugify("please create a the and or"), "project")

    def test_preserves_meaningful_verbs(self):
        self.assertEqual(slugify("Fix the login bug"), "fix-login-bug")


class TestCreateProjectStructure(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_creates_all_subdirs(self):
        paths = create_project_structure(self.tmpdir, "Create weather app")
        self.assertTrue(os.path.isdir(paths["docs"]))
        self.assertTrue(os.path.isdir(paths["src"]))
        self.assertTrue(os.path.isdir(paths["reviews"]))
        self.assertTrue(os.path.isdir(paths["tests"]))

    def test_paths_are_under_root(self):
        paths = create_project_structure(self.tmpdir, "Create weather app")
        for key in ("docs", "src", "reviews", "tests"):
            self.assertTrue(paths[key].startswith(paths["root"]))

    def test_duplicate_gets_unique_suffix(self):
        paths1 = create_project_folder(self.tmpdir, "Create weather app")
        paths2 = create_project_folder(self.tmpdir, "Create weather app")
        self.assertNotEqual(paths1["root"], paths2["root"])
        self.assertTrue(paths2["root"].endswith("-2"))

    def test_root_name_is_slug(self):
        paths = create_project_structure(self.tmpdir, "Build a todo list")
        self.assertTrue(paths["root"].endswith("todo-list"))

    def test_without_subdirs(self):
        paths = create_project_folder(self.tmpdir, "Review PR", with_subdirs=False)
        self.assertIn("root", paths)
        self.assertNotIn("docs", paths)
        self.assertNotIn("src", paths)
        self.assertTrue(os.path.isdir(paths["root"]))


if __name__ == "__main__":
    unittest.main()
