"""Tests for config loader."""

import os
import tempfile
import unittest

from config_loader import load_config


class TestConfigLoader(unittest.TestCase):
    def test_load_missing_config_returns_defaults(self):
        config = load_config("nonexistent_file_xyz.yaml")
        self.assertIn("kiro", config)
        self.assertIn("workers", config)
        self.assertEqual(config["kiro"]["cli_path"], "kiro-cli")

    def test_load_valid_yaml(self):
        content = "kiro:\n  cli_path: /usr/bin/kiro\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(content)
            f.flush()
            config = load_config(f.name)

        self.assertEqual(config["kiro"]["cli_path"], "/usr/bin/kiro")
        os.unlink(f.name)

    def test_load_example_fallback(self):
        # config.yaml.example exists in our project
        config = load_config("config.yaml")
        self.assertIn("kiro", config)


if __name__ == "__main__":
    unittest.main()
