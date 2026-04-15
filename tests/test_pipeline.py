"""Tests for the collaboration pipeline."""

import unittest
from unittest.mock import patch, MagicMock

from orchestrator.pipeline import CollaborationPipeline
from orchestrator.router import TaskPlan
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


@patch(P[7])
@patch(P[6])
@patch(P[5])
@patch(P[4])
@patch(P[3])
@patch(P[2])
@patch(P[1])
@patch(P[0])
class TestCollaborationPipeline(unittest.TestCase):
    def test_single_worker_pipeline(self, mock_popen, *_ui):
        mock_popen.return_value = _mock_popen(["Done"])
        workers = {"developer": DeveloperWorker()}
        pipeline = CollaborationPipeline(workers)

        plan = TaskPlan(primary_worker="developer")
        results = pipeline.run(plan, "Build feature X")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].worker_name, "Developer")

    def test_missing_primary_worker(self, mock_popen, *_ui):
        workers = {"developer": DeveloperWorker()}
        pipeline = CollaborationPipeline(workers)

        plan = TaskPlan(primary_worker="nonexistent")
        results = pipeline.run(plan, "Do something")

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].success)

    def test_preparation_workers_run_first(self, mock_popen, *_ui):
        mock_popen.return_value = _mock_popen(["refined task output"])
        workers = {
            "product_owner": ProductOwnerWorker(),
            "developer": DeveloperWorker(),
        }
        pipeline = CollaborationPipeline(workers)

        plan = TaskPlan(
            primary_worker="developer",
            preparation_workers=["product_owner"],
            collaboration_needed=True,
        )
        results = pipeline.run(plan, "Make a weather app")

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

        plan = TaskPlan(
            primary_worker="developer",
            preparation_workers=["product_owner", "business_analyst"],
            design_worker="architect",
            review_workers=["reviewer", "code_owner"],
            qa_worker="qa",
            collaboration_needed=True,
        )
        results = pipeline.run(plan, "Create a weather app")

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

        plan = TaskPlan(
            primary_worker="developer",
            review_workers=["reviewer"],
            qa_worker=None,
            collaboration_needed=True,
        )
        results = pipeline.run(plan, "Fix something")

        names = [r.worker_name for r in results]
        self.assertEqual(names[0], "Developer")
        self.assertEqual(names[1], "Reviewer")
        self.assertEqual(names[2], "Developer")  # fix pass


if __name__ == "__main__":
    unittest.main()
