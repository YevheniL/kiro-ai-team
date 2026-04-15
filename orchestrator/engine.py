"""
Orchestrator - Routes tasks to workers and manages collaboration.

Analyzes user requests, determines which worker(s) to involve,
and coordinates their interaction. Shows routing decisions in real time.
"""

from workers.base import WorkerResult
from workers.developer import DeveloperWorker
from workers.qa import QAWorker
from workers.architect import ArchitectWorker
from workers.code_owner import CodeOwnerWorker
from workers.reviewer import ReviewerWorker
from workers.product_owner import ProductOwnerWorker
from workers.business_analyst import BusinessAnalystWorker
from orchestrator.router import TaskRouter
from orchestrator.pipeline import CollaborationPipeline
from ui.console import print_routing


class Orchestrator:
    def __init__(self, config: dict):
        self.config = config
        self.project_path = config.get("project", {}).get("default_path", ".")
        self.workers = self._init_workers()
        self.router = TaskRouter()
        self.pipeline = CollaborationPipeline(self.workers)
        self.conversation_history: list[dict] = []

    def _init_workers(self) -> dict:
        worker_config = self.config.get("workers", {})
        kiro_config = self.config.get("kiro", {})
        workers = {}

        worker_classes = {
            "developer": DeveloperWorker,
            "qa": QAWorker,
            "architect": ArchitectWorker,
            "code_owner": CodeOwnerWorker,
            "reviewer": ReviewerWorker,
            "product_owner": ProductOwnerWorker,
            "business_analyst": BusinessAnalystWorker,
        }

        for name, cls in worker_classes.items():
            cfg = worker_config.get(name, {})
            if cfg.get("enabled", True):
                workers[name] = cls(
                    kiro_cli=kiro_config.get("cli_path", "kiro-cli"),
                    project_path=self.project_path,
                )
        return workers

    def execute(self, task: str) -> str:
        """Execute a task by routing to appropriate worker(s)."""
        self.conversation_history.append({"role": "user", "content": task})

        plan = self.router.route(task)

        # Resolve display names
        primary_worker = self.workers.get(plan.primary_worker)
        primary_display = primary_worker.name if primary_worker else plan.primary_worker
        supporting_display = [
            self.workers[w].name for w in plan.supporting_workers
            if w in self.workers
        ]
        preparation_display = [
            self.workers[w].name for w in plan.preparation_workers
            if w in self.workers
        ]
        design_display = None
        if plan.design_worker and plan.design_worker in self.workers:
            design_display = self.workers[plan.design_worker].name
        review_display = [
            self.workers[w].name for w in plan.review_workers
            if w in self.workers
        ]
        qa_display = None
        if plan.qa_worker and plan.qa_worker in self.workers:
            qa_display = self.workers[plan.qa_worker].name

        print_routing(
            plan.task_type, primary_display,
            supporting_display, plan.collaboration_needed,
            preparation=preparation_display,
            designer=design_display,
            reviewers=review_display,
            qa=qa_display,
        )

        if plan.collaboration_needed or plan.preparation_workers or plan.design_worker or plan.review_workers or plan.qa_worker:
            result = self.pipeline.run(plan, task)
        else:
            worker = self.workers.get(plan.primary_worker)
            if not worker:
                return f"❌ Worker '{plan.primary_worker}' is not available."
            result = worker.execute(task, self.project_path)

        response = self._format_result(plan, result)
        self.conversation_history.append({"role": "assistant", "content": response})
        return response

    def _format_result(self, plan, result) -> str:
        if isinstance(result, list):
            parts = []
            for r in result:
                parts.append(f"[{r.worker_name}]\n{r.output}")
            return "\n\n---\n\n".join(parts)

        if isinstance(result, WorkerResult):
            return f"[{result.worker_name}]\n{result.output}"

        return str(result)
