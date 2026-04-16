"""Tests for the collaboration pipeline."""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from orchestrator.pipeline import CollaborationPipeline
from orchestrator.router import TaskPlan
from project_scaffold import create_project_folder
from workers.developer import DeveloperWorker
from workers.qa import QAWorker
from workers.reviewer import ReviewerWorker
from workers.code_owner import CodeOwnerWorker
from workers.product_owner import ProductOwnerWorker
from workers.business_analyst import BusinessAnalystWorker
from workers.architect import ArchitectWorker
from workers.base import WorkerResult


def _mock_popen(stdout_lines, returncode=0):
    mock_proc = MagicMock()
    mock_proc.stdout = iter(line.encode("utf-8") + b"\n" for line in stdout_lines)
    mock_proc.wait.return_value = returncode
    mock_proc.returncode = returncode
    return mock_proc


P = [
    "workers.base.subprocess.Popen",
    "workers.base.print_worker_start",
    "workers.base.print_worker_stream",
    "workers.base.print_worker_done",
    "workers.base.print_worker_retry",
    "orchestrator.pipeline.print_handoff",
    "orchestrator.pipeline.print_summary",
    "orchestrator.pipeline.print_phase",
]


def _make_paths(tmpdir, task, with_subdirs=True):
    """Helper to create a project folder and return paths dict."""
    return create_project_folder(tmpdir, task, with_subdirs=with_subdirs)


@patch(P[7])
@patch(P[6])
@patch(P[5])
@patch(P[4])
@patch(P[3])
@patch(P[2])
@patch(P[1])
@patch(P[0])
class TestCollaborationPipeline(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_single_worker_pipeline(self, mock_popen, *_ui):
        mock_popen.return_value = _mock_popen(["Done"])
        workers = {"developer": DeveloperWorker()}
        pipeline = CollaborationPipeline(workers)
        paths = _make_paths(self.tmpdir, "Build feature X", with_subdirs=False)

        plan = TaskPlan(primary_worker="developer")
        results = pipeline.run(plan, "Build feature X", paths)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].worker_name, "Developer")

    def test_missing_primary_worker(self, mock_popen, *_ui):
        workers = {"developer": DeveloperWorker()}
        pipeline = CollaborationPipeline(workers)
        paths = _make_paths(self.tmpdir, "Do something", with_subdirs=False)

        plan = TaskPlan(primary_worker="nonexistent")
        results = pipeline.run(plan, "Do something", paths)

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].success)

    def test_preparation_workers_run_first(self, mock_popen, *_ui):
        mock_popen.return_value = _mock_popen(["refined task output"])
        workers = {
            "product_owner": ProductOwnerWorker(),
            "developer": DeveloperWorker(),
        }
        pipeline = CollaborationPipeline(workers)
        paths = _make_paths(self.tmpdir, "Make a weather app")

        plan = TaskPlan(
            primary_worker="developer",
            preparation_workers=["product_owner"],
            collaboration_needed=True,
        )
        results = pipeline.run(plan, "Make a weather app", paths)

        self.assertEqual(results[0].worker_name, "Product Owner")
        self.assertEqual(results[1].worker_name, "Developer")

    def test_full_dev_pipeline(self, mock_popen, *_ui):
        """PO → BA → Architect → Dev → Reviewer → Code Owner → Dev (fix) → QA"""
        mock_popen.return_value = _mock_popen(["output"])
        workers = {
            "product_owner": ProductOwnerWorker(),
            "business_analyst": BusinessAnalystWorker(),
            "architect": ArchitectWorker(),
            "developer": DeveloperWorker(),
            "reviewer": ReviewerWorker(),
            "code_owner": CodeOwnerWorker(),
            "qa": QAWorker(),
        }
        pipeline = CollaborationPipeline(workers)
        paths = _make_paths(self.tmpdir, "Create a weather app")

        plan = TaskPlan(
            primary_worker="developer",
            preparation_workers=["product_owner", "business_analyst"],
            design_worker="architect",
            review_workers=["reviewer", "code_owner"],
            qa_worker="qa",
            collaboration_needed=True,
        )
        results = pipeline.run(plan, "Create a weather app", paths)

        names = [r.worker_name for r in results]
        self.assertEqual(names[0], "Product Owner")
        self.assertEqual(names[1], "Business Analyst")
        self.assertEqual(names[2], "Architect")
        self.assertEqual(names[3], "Developer")
        self.assertEqual(names[4], "Reviewer")
        self.assertEqual(names[5], "Code Owner")
        self.assertEqual(names[6], "Developer")  # fix pass
        self.assertEqual(names[7], "QA")
        self.assertEqual(len(names), 8)

    def test_review_without_qa(self, mock_popen, *_ui):
        mock_popen.return_value = _mock_popen(["output"])
        workers = {
            "developer": DeveloperWorker(),
            "reviewer": ReviewerWorker(),
        }
        pipeline = CollaborationPipeline(workers)
        paths = _make_paths(self.tmpdir, "Fix something", with_subdirs=False)

        plan = TaskPlan(
            primary_worker="developer",
            review_workers=["reviewer"],
            qa_worker=None,
            collaboration_needed=True,
        )
        results = pipeline.run(plan, "Fix something", paths)

        names = [r.worker_name for r in results]
        self.assertEqual(names[0], "Developer")
        self.assertEqual(names[1], "Reviewer")
        self.assertEqual(names[2], "Developer")  # fix pass

    def test_project_folder_has_all_subdirs(self, mock_popen, *_ui):
        """Development tasks should have docs/, src/, reviews/, tests/."""
        paths = _make_paths(self.tmpdir, "Create a weather app")

        self.assertTrue(os.path.isdir(paths["root"]))
        self.assertTrue(os.path.isdir(paths["docs"]))
        self.assertTrue(os.path.isdir(paths["src"]))
        self.assertTrue(os.path.isdir(paths["reviews"]))
        self.assertTrue(os.path.isdir(paths["tests"]))

    def test_all_workers_run_from_project_root(self, mock_popen, *_ui):
        """All workers should run from the project root (for agent resolution)."""
        mock_popen.return_value = _mock_popen(["output"])
        workers = {
            "product_owner": ProductOwnerWorker(),
            "developer": DeveloperWorker(),
            "reviewer": ReviewerWorker(),
        }
        pipeline = CollaborationPipeline(workers)
        paths = _make_paths(self.tmpdir, "Create a todo app")

        plan = TaskPlan(
            primary_worker="developer",
            preparation_workers=["product_owner"],
            review_workers=["reviewer"],
            collaboration_needed=True,
            task_type="development",
        )
        pipeline.run(plan, "Create a todo app", paths)

        abs_root = os.path.abspath(paths["root"])
        cwds = [call.kwargs.get("cwd") for call in mock_popen.call_args_list]
        for cwd in cwds:
            self.assertEqual(cwd, abs_root,
                             f"Expected all cwds to be project root {abs_root}, got {cwd}")

    def test_prompts_contain_subfolder_paths(self, mock_popen, *_ui):
        """Worker prompts should reference the correct subfolder paths."""
        mock_popen.return_value = _mock_popen(["output"])
        workers = {
            "developer": DeveloperWorker(),
            "reviewer": ReviewerWorker(),
            "qa": QAWorker(),
        }
        pipeline = CollaborationPipeline(workers)
        paths = _make_paths(self.tmpdir, "Build feature Y")

        plan = TaskPlan(
            primary_worker="developer",
            review_workers=["reviewer"],
            qa_worker="qa",
            collaboration_needed=True,
        )
        pipeline.run(plan, "Build feature Y", paths)

        # Collect all prompts (last arg of each Popen call)
        prompts = [call[0][0][-1] for call in mock_popen.call_args_list]

        # Developer prompt should mention src/
        self.assertTrue(any("src/" in p for p in prompts),
                        "Expected 'src/' in developer prompt")
        # Reviewer prompt should mention reviews/
        self.assertTrue(any("reviews/" in p for p in prompts),
                        "Expected 'reviews/' in reviewer prompt")
        # QA prompt should mention tests/
        self.assertTrue(any("tests/" in p for p in prompts),
                        "Expected 'tests/' in QA prompt")

    def test_non_dev_task_uses_root_only(self, mock_popen, *_ui):
        """Non-development tasks should use root path without subdirs."""
        mock_popen.return_value = _mock_popen(["output"])
        workers = {"qa": QAWorker()}
        pipeline = CollaborationPipeline(workers)
        paths = _make_paths(self.tmpdir, "Test checkout flow", with_subdirs=False)

        plan = TaskPlan(primary_worker="qa", task_type="quality")
        pipeline.run(plan, "Test checkout flow", paths)

        self.assertTrue(os.path.isdir(paths["root"]))
        self.assertNotIn("docs", paths)
        self.assertNotIn("src", paths)

    def test_save_instructions_in_prompts(self, mock_popen, *_ui):
        """Worker prompts should include file-save instructions."""
        mock_popen.return_value = _mock_popen(["output"])
        workers = {
            "product_owner": ProductOwnerWorker(),
            "developer": DeveloperWorker(),
        }
        pipeline = CollaborationPipeline(workers)
        paths = _make_paths(self.tmpdir, "Build app")

        plan = TaskPlan(
            primary_worker="developer",
            preparation_workers=["product_owner"],
            collaboration_needed=True,
        )
        pipeline.run(plan, "Build app", paths)

        # Check that the PO prompt includes the save instruction
        first_call_args = mock_popen.call_args_list[0][0][0]  # first Popen positional arg
        prompt_text = first_call_args[-1]  # last element is the prompt
        self.assertIn("docs/requirements.md", prompt_text)


if __name__ == "__main__":
    unittest.main()
