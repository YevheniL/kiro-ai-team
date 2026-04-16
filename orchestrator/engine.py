"""
Orchestrator - Routes tasks to workers and manages collaboration.

Analyzes user requests, determines which worker(s) to involve,
and coordinates their interaction. Shows routing decisions in real time.
"""

import os
import shutil

from project_scaffold import create_project_folder
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

# Task types that produce code and benefit from the full folder layout
_CODE_TASK_TYPES = {"development", "cli-development", "general"}


class Orchestrator:
    def __init__(self, config: dict):
        self.config = config
        self.project_path = config.get("project", {}).get("default_path", ".")
        self.output_dir = config.get("project", {}).get("output_dir", "projects")
        self.workers = self._init_workers()
        self.router = TaskRouter()
        self.pipeline = CollaborationPipeline(self.workers)
        self.conversation_history: list[dict] = []

    def _resolve_output_base(self) -> str:
        """Return the absolute path to the output directory, creating it.

        Falls back to ./output_dir if the configured project path doesn't
        exist and can't be created (e.g. unedited placeholder in config).
        """
        base = os.path.join(self.project_path, self.output_dir)
        try:
            os.makedirs(base, exist_ok=True)
        except OSError:
            # Configured path is invalid — fall back to cwd
            base = os.path.join(".", self.output_dir)
            os.makedirs(base, exist_ok=True)
            print(f"⚠️  Could not create '{self.project_path}/{self.output_dir}', "
                  f"using './{self.output_dir}' instead.\n"
                  f"   Update project.default_path in config.yaml to fix this.\n")
        return os.path.abspath(base)

    @staticmethod
    def _ensure_agents(project_root: str) -> None:
        """Copy .kiro/agents/ into the project root so kiro-cli can find them.

        kiro-cli resolves agents relative to cwd by walking up to find
        .kiro/agents/. Since workers run inside subfolders (docs/, src/, etc.),
        the agents must exist at or above the project root.
        """
        target = os.path.join(project_root, ".kiro", "agents")
        if os.path.isdir(target):
            return  # already there

        # Look for agents in common locations
        candidates = [
            os.path.join(".", ".kiro", "agents"),           # workspace root
            os.path.join(os.path.dirname(__file__), "..", ".kiro", "agents"),
            os.path.join(".", "agents"),                    # source agent configs
        ]
        for src in candidates:
            src = os.path.normpath(src)
            if os.path.isdir(src):
                os.makedirs(target, exist_ok=True)
                for f in os.listdir(src):
                    if f.endswith(".json"):
                        shutil.copy2(os.path.join(src, f), target)
                return

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

        # Create a dedicated project folder for this task
        output_base = self._resolve_output_base()
        with_subdirs = plan.task_type in _CODE_TASK_TYPES
        paths = create_project_folder(output_base, task, with_subdirs=with_subdirs)
        self._ensure_agents(paths["root"])
        print(f"\n📁 Project folder: {os.path.abspath(paths['root'])}\n")

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

        if (plan.collaboration_needed or plan.preparation_workers
                or plan.design_worker or plan.review_workers or plan.qa_worker):
            result = self.pipeline.run(plan, task, paths)
        else:
            worker = self.workers.get(plan.primary_worker)
            if not worker:
                return f"❌ Worker '{plan.primary_worker}' is not available."
            result = worker.execute(task, paths["root"])

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
