"""Tests for Kiro CLI agent configuration files."""

import json
import os
import unittest


AGENTS_DIR = os.path.join(os.path.dirname(__file__), "..", "agents")
REQUIRED_FIELDS = ["name", "description", "tools", "allowedTools", "prompt"]
EXPECTED_AGENTS = ["developer", "qa", "architect", "code-owner", "reviewer", "product-owner", "business-analyst"]


class TestAgentConfigs(unittest.TestCase):
    def test_all_agent_files_exist(self):
        for agent in EXPECTED_AGENTS:
            path = os.path.join(AGENTS_DIR, f"{agent}.json")
            self.assertTrue(os.path.exists(path), f"Missing agent config: {agent}.json")

    def test_agent_configs_are_valid_json(self):
        for agent in EXPECTED_AGENTS:
            path = os.path.join(AGENTS_DIR, f"{agent}.json")
            with open(path) as f:
                data = json.load(f)
            for field in REQUIRED_FIELDS:
                self.assertIn(field, data, f"{agent}.json missing field: {field}")

    def test_agent_names_match_filenames(self):
        for agent in EXPECTED_AGENTS:
            path = os.path.join(AGENTS_DIR, f"{agent}.json")
            with open(path) as f:
                data = json.load(f)
            self.assertEqual(data["name"], agent)

    def test_all_agents_have_read_tool(self):
        """Every agent should at least be able to read files."""
        for agent in EXPECTED_AGENTS:
            path = os.path.join(AGENTS_DIR, f"{agent}.json")
            with open(path) as f:
                data = json.load(f)
            self.assertIn("read", data["tools"], f"{agent} missing 'read' tool")

    def test_developer_has_write_tool(self):
        path = os.path.join(AGENTS_DIR, "developer.json")
        with open(path) as f:
            data = json.load(f)
        self.assertIn("write", data["tools"])
        self.assertIn("write", data["allowedTools"])

    def test_code_owner_is_read_only(self):
        """Code owner should only read, not write."""
        path = os.path.join(AGENTS_DIR, "code-owner.json")
        with open(path) as f:
            data = json.load(f)
        self.assertNotIn("write", data["tools"])

    def test_creative_agents_can_write(self):
        """Developer, QA, Architect, PO, and BA need write access to create files."""
        for agent in ["developer", "qa", "architect", "product-owner", "business-analyst"]:
            path = os.path.join(AGENTS_DIR, f"{agent}.json")
            with open(path) as f:
                data = json.load(f)
            self.assertIn("write", data["tools"], f"{agent} should have write tool")
            self.assertIn("write", data["allowedTools"], f"{agent} should have write auto-approved")

    def test_reviewer_is_read_only(self):
        """Reviewer should not write files."""
        path = os.path.join(AGENTS_DIR, "reviewer.json")
        with open(path) as f:
            data = json.load(f)
        self.assertNotIn("write", data["tools"])


if __name__ == "__main__":
    unittest.main()
