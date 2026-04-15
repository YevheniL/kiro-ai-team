"""Tests for worker initialization and prompts."""

import unittest
from unittest.mock import patch, MagicMock

from workers.developer import DeveloperWorker
from workers.qa import QAWorker
from workers.architect import ArchitectWorker
from workers.code_owner import CodeOwnerWorker
from workers.reviewer import ReviewerWorker
from workers.product_owner import ProductOwnerWorker
from workers.business_analyst import BusinessAnalystWorker
from workers.base import WorkerResult


def _mock_popen(stdout_lines: list[str], returncode: int = 0):
    """Create a mock Popen that yields raw bytes (matching binary mode)."""
    mock_proc = MagicMock()
    mock_proc.stdout = iter(line.encode("utf-8") + b"\n" for line in stdout_lines)
    mock_proc.wait.return_value = returncode
    mock_proc.returncode = returncode
    return mock_proc


class TestWorkerPrompts(unittest.TestCase):
    """Verify each worker has a proper system prompt."""

    def test_developer_prompt(self):
        w = DeveloperWorker()
        prompt = w.get_system_prompt()
        self.assertIn("Developer", prompt)
        self.assertIn("DEPENDENCY POLICY", prompt)
        self.assertIn("UI POLICY", prompt)
        self.assertIn("review comments", prompt.lower())

    def test_qa_prompt(self):
        w = QAWorker()
        prompt = w.get_system_prompt()
        self.assertIn("QA", prompt)
        self.assertIn("test", prompt.lower())
        self.assertIn("verdict", prompt.lower())

    def test_architect_prompt(self):
        w = ArchitectWorker()
        prompt = w.get_system_prompt()
        self.assertIn("Architect", prompt)
        self.assertIn("DEPENDENCY POLICY", prompt)

    def test_code_owner_prompt(self):
        w = CodeOwnerWorker()
        prompt = w.get_system_prompt()
        self.assertIn("Code Owner", prompt)
        self.assertIn("DEPENDENCY POLICY", prompt)

    def test_reviewer_prompt(self):
        w = ReviewerWorker()
        prompt = w.get_system_prompt()
        self.assertIn("Reviewer", prompt)
        self.assertIn("DEPENDENCY POLICY", prompt)

    def test_product_owner_prompt(self):
        w = ProductOwnerWorker()
        prompt = w.get_system_prompt()
        self.assertIn("Product Owner", prompt)
        self.assertIn("DEPENDENCY POLICY", prompt)
        self.assertIn("UI POLICY", prompt)
        self.assertIn("GUI", prompt)

    def test_business_analyst_prompt(self):
        w = BusinessAnalystWorker()
        prompt = w.get_system_prompt()
        self.assertIn("Business Analyst", prompt)
        self.assertIn("DEPENDENCY POLICY", prompt)
        self.assertIn("open-source", prompt.lower())


class TestWorkerExecution(unittest.TestCase):
    """Test worker execution with mocked kiro-cli (streaming Popen)."""

    @patch("workers.base.subprocess.Popen")
    @patch("workers.base.print_worker_done")
    @patch("workers.base.print_worker_stream")
    @patch("workers.base.print_worker_start")
    @patch("workers.base.print_worker_retry")
    def test_developer_execute_success(self, _retry, _start, _stream, _done, mock_popen):
        mock_popen.return_value = _mock_popen(
            ["Feature implemented successfully."], returncode=0
        )
        w = DeveloperWorker(kiro_cli="kiro-cli", project_path="/tmp/project")
        result = w.execute("Implement login", "/tmp/project")

        self.assertIsInstance(result, WorkerResult)
        self.assertTrue(result.success)
        self.assertEqual(result.worker_name, "Developer")
        self.assertIn("implemented", result.output)
        self.assertEqual(result.retries, 0)

    @patch("workers.base.subprocess.Popen")
    @patch("workers.base.print_worker_done")
    @patch("workers.base.print_worker_stream")
    @patch("workers.base.print_worker_start")
    @patch("workers.base.print_worker_retry")
    def test_worker_handles_kiro_failure_with_retries(self, mock_retry, _start, _stream, _done, mock_popen):
        # All attempts fail
        mock_popen.return_value = _mock_popen(["error output"], returncode=1)
        w = QAWorker(kiro_cli="kiro-cli", project_path="/tmp/project", max_retries=1)
        result = w.execute("Test login", "/tmp/project")

        self.assertIsInstance(result, WorkerResult)
        self.assertFalse(result.success)
        self.assertIn("Error", result.output)
        # Should have retried
        self.assertEqual(result.retries, 1)

    @patch("workers.base.subprocess.Popen")
    @patch("workers.base.print_worker_done")
    @patch("workers.base.print_worker_stream")
    @patch("workers.base.print_worker_start")
    @patch("workers.base.print_worker_retry")
    def test_worker_recovers_on_retry(self, mock_retry, _start, _stream, _done, mock_popen):
        # First call fails, second succeeds
        fail_proc = _mock_popen(["fail"], returncode=1)
        ok_proc = _mock_popen(["Success on retry"], returncode=0)
        mock_popen.side_effect = [fail_proc, ok_proc]

        w = DeveloperWorker(kiro_cli="kiro-cli", project_path=".", max_retries=1)
        result = w.execute("Do stuff", ".")

        self.assertTrue(result.success)
        self.assertEqual(result.retries, 1)
        self.assertIn("Success on retry", result.output)

    @patch("workers.base.subprocess.Popen")
    @patch("workers.base.print_worker_done")
    @patch("workers.base.print_worker_stream")
    @patch("workers.base.print_worker_start")
    @patch("workers.base.print_worker_retry")
    def test_worker_passes_project_path_and_agent(self, _retry, _start, _stream, _done, mock_popen):
        mock_popen.return_value = _mock_popen(["ok"], returncode=0)
        w = DeveloperWorker(kiro_cli="kiro-cli", project_path="/my/android/app")
        w.execute("Fix crash", "/my/android/app")

        call_args = mock_popen.call_args[0][0]
        self.assertIn("chat", call_args)
        self.assertIn("--no-interactive", call_args)
        self.assertIn("--trust-all-tools", call_args)
        self.assertIn("--agent", call_args)
        self.assertIn("developer", call_args)

    @patch("workers.base.subprocess.Popen")
    @patch("workers.base.print_worker_done")
    @patch("workers.base.print_worker_stream")
    @patch("workers.base.print_worker_start")
    @patch("workers.base.print_worker_retry")
    def test_streaming_calls_print_for_each_line(self, _retry, mock_start, mock_stream, _done, mock_popen):
        mock_popen.return_value = _mock_popen(
            ["line 1", "line 2", "line 3"], returncode=0
        )
        w = DeveloperWorker(kiro_cli="kiro-cli", project_path=".")
        w.execute("Do stuff", ".")

        mock_start.assert_called_once()
        self.assertEqual(mock_stream.call_count, 3)

    @patch("workers.base.subprocess.Popen")
    @patch("workers.base.print_worker_done")
    @patch("workers.base.print_worker_stream")
    @patch("workers.base.print_worker_start")
    @patch("workers.base.print_worker_retry")
    def test_handles_unicode_in_output(self, _retry, _start, _stream, _done, mock_popen):
        """Verify UTF-8 decoding with replacement handles bad bytes."""
        mock_proc = MagicMock()
        mock_proc.stdout = iter([
            "Hello world\n".encode("utf-8"),
            b"Bad byte: \x98 here\n",  # The charmap error from the bug report
            "Normal line\n".encode("utf-8"),
        ])
        mock_proc.wait.return_value = 0
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        w = DeveloperWorker(kiro_cli="kiro-cli", project_path=".")
        result = w.execute("Do stuff", ".")

        self.assertTrue(result.success)
        # The bad byte should be replaced, not crash
        self.assertIn("Hello world", result.output)
        self.assertIn("Normal line", result.output)


if __name__ == "__main__":
    unittest.main()
