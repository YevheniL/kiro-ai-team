"""Tests for the task router."""

import unittest
from orchestrator.router import TaskRouter


class TestTaskRouter(unittest.TestCase):
    def setUp(self):
        self.router = TaskRouter()

    # --- PR Review routing ---
    def test_pr_review_routes_to_reviewer(self):
        plan = self.router.route("Review PR #123")
        self.assertEqual(plan.primary_worker, "reviewer")
        self.assertTrue(plan.collaboration_needed)

    def test_pr_review_no_preparation(self):
        plan = self.router.route("Review PR #123")
        self.assertEqual(plan.preparation_workers, [])

    # --- Development routing ---
    def test_implement_routes_to_developer(self):
        plan = self.router.route("Implement login screen")
        self.assertEqual(plan.primary_worker, "developer")

    def test_fix_bug_routes_to_developer(self):
        plan = self.router.route("Fix bug in payment flow")
        self.assertEqual(plan.primary_worker, "developer")

    def test_create_feature_routes_to_developer(self):
        plan = self.router.route("Create feature for user profiles")
        self.assertEqual(plan.primary_worker, "developer")

    def test_development_has_preparation(self):
        plan = self.router.route("Implement login screen")
        self.assertIn("product_owner", plan.preparation_workers)
        self.assertIn("business_analyst", plan.preparation_workers)

    def test_development_has_review_loop(self):
        plan = self.router.route("Create a weather app")
        self.assertIn("reviewer", plan.review_workers)
        self.assertIn("code_owner", plan.review_workers)
        self.assertEqual(plan.qa_worker, "qa")
        self.assertEqual(plan.design_worker, "architect")

    def test_development_no_supporting(self):
        """Dev tasks use design + review + qa, not supporting."""
        plan = self.router.route("Create a weather app")
        self.assertEqual(plan.supporting_workers, [])

    # --- Architecture routing ---
    def test_architecture_routes_to_architect(self):
        plan = self.router.route("Design the architecture for notifications")
        self.assertEqual(plan.primary_worker, "architect")

    def test_proposal_routes_to_architect(self):
        plan = self.router.route("Create a proposal for the new module")
        self.assertEqual(plan.primary_worker, "architect")

    def test_architecture_has_po_preparation(self):
        plan = self.router.route("Design the architecture for notifications")
        self.assertIn("product_owner", plan.preparation_workers)

    # --- QA routing ---
    def test_test_routes_to_qa(self):
        plan = self.router.route("Test the checkout flow")
        self.assertEqual(plan.primary_worker, "qa")
        self.assertFalse(plan.collaboration_needed)

    def test_coverage_routes_to_qa(self):
        plan = self.router.route("Check test coverage for utils")
        self.assertEqual(plan.primary_worker, "qa")

    def test_qa_no_preparation(self):
        plan = self.router.route("Test the checkout flow")
        self.assertEqual(plan.preparation_workers, [])

    # --- Investigation routing ---
    def test_investigate_routes_to_architect(self):
        plan = self.router.route("Investigate the legacy payment module")
        self.assertEqual(plan.primary_worker, "architect")

    def test_investigation_has_ba_preparation(self):
        plan = self.router.route("Investigate the legacy payment module")
        self.assertIn("business_analyst", plan.preparation_workers)

    # --- Requirements routing ---
    def test_jira_routes_to_product_owner(self):
        plan = self.router.route("Create a jira ticket for the new feature")
        self.assertEqual(plan.primary_worker, "product_owner")

    def test_story_routes_to_product_owner(self):
        plan = self.router.route("Write a user story for checkout")
        self.assertEqual(plan.primary_worker, "product_owner")

    # --- CLI development routing ---
    def test_script_routes_to_cli_development(self):
        plan = self.router.route("Write a script to parse logs")
        self.assertEqual(plan.task_type, "cli-development")
        self.assertEqual(plan.primary_worker, "developer")

    # --- Default routing ---
    def test_unknown_task_defaults_to_developer(self):
        plan = self.router.route("Do something random")
        self.assertEqual(plan.primary_worker, "developer")
        self.assertIn("product_owner", plan.preparation_workers)
        self.assertIn("reviewer", plan.review_workers)
        self.assertEqual(plan.qa_worker, "qa")
        self.assertEqual(plan.design_worker, "architect")

    # --- Task types ---
    def test_pr_review_task_type(self):
        plan = self.router.route("Review PR #42")
        self.assertEqual(plan.task_type, "pr-review")

    def test_development_task_type(self):
        plan = self.router.route("Implement dark mode")
        self.assertEqual(plan.task_type, "development")

    def test_requirements_task_type(self):
        plan = self.router.route("Write a jira ticket")
        self.assertEqual(plan.task_type, "requirements")


if __name__ == "__main__":
    unittest.main()
