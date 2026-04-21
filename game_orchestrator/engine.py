"""
Game Orchestrator - Routes game tasks to workers and manages collaboration.

Analyzes user requests, determines which game worker(s) to involve,
and coordinates their interaction. Shows routing decisions in real time.
"""

import os
import shutil

from project_scaffold import create_project_folder
from workers.base import WorkerResult
from workers.game_developer import GameDeveloperWorker
from workers.game_qa import GameQAWorker
from workers.game_architect import GameArchitectWorker
from workers.game_code_owner import GameCodeOwnerWorker
from workers.game_reviewer import GameReviewerWorker
from workers.game_product_owner import GameProductOwnerWorker
from workers.game_business_analyst import GameBusinessAnalystWorker
from workers.game_designer import GameDesignerWorker
from workers.screenwriter import ScreenwriterWorker
from workers.level_designer import LevelDesignerWorker
from workers.artist import ArtistWorker
from workers.graphical_designer import GraphicalDesignerWorker
from game_orchestrator.router import GameTaskRouter
from game_orchestrator.pipeline import GameCollaborationPipeline
from ui.console import print_routing

# Task types that produce code and benefit from the full folder layout
_CODE_TASK_TYPES = {"development", "general"}


class GameOrchestrator:
    def __init__(self, config: dict):
        self.config = config
        self.project_path = config.get("project", {}).get("default_path", ".")
        self.output_dir = config.get("project", {}).get("output_dir", "projects")
        self.workers = self._init_workers()
        self.router = GameTaskRouter()
        self.pipeline = GameCollaborationPipeline(self.workers)
        self.conversation_history: list[dict] = []

    def _resolve_output_base(self) -> str:
        base = os.path.join(self.project_path, self.output_dir)
        try:
            os.makedirs(base, exist_ok=True)
        except OSError:
            base = os.path.join(".", self.output_dir)
            os.makedirs(base, exist_ok=True)
            print(f"⚠️  Could not create '{self.project_path}/{self.output_dir}', "
                  f"using './{self.output_dir}' instead.\n"
                  f"   Update project.default_path in config.yaml to fix this.\n")
        return os.path.abspath(base)

    @staticmethod
    def _ensure_agents(project_root: str) -> None:
        target = os.path.join(project_root, ".kiro", "agents")
        if os.path.isdir(target):
            return

        candidates = [
            os.path.join(".", ".kiro", "agents"),
            os.path.join(os.path.dirname(__file__), "..", ".kiro", "agents"),
            os.path.join(".", "agents"),
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
            "game_developer": GameDeveloperWorker,
            "game_qa": GameQAWorker,
            "game_architect": GameArchitectWorker,
            "game_code_owner": GameCodeOwnerWorker,
            "game_reviewer": GameReviewerWorker,
            "game_product_owner": GameProductOwnerWorker,
            "game_business_analyst": GameBusinessAnalystWorker,
            "game_designer": GameDesignerWorker,
            "screenwriter": ScreenwriterWorker,
            "level_designer": LevelDesignerWorker,
            "artist": ArtistWorker,
            "graphical_designer": GraphicalDesignerWorker,
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
        self.conversation_history.append({"role": "user", "content": task})

        plan = self.router.route(task)

        output_base = self._resolve_output_base()
        with_subdirs = plan.task_type in _CODE_TASK_TYPES
        paths = create_project_folder(output_base, task, with_subdirs=with_subdirs)
        # Also create design/ subfolder for game projects
        if with_subdirs:
            design_dir = os.path.join(paths["root"], "design")
            os.makedirs(design_dir, exist_ok=True)
            paths["design"] = design_dir
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
        creative_display = [
            self.workers[w].name for w in plan.creative_workers
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
        # Show creative team if present
        if creative_display:
            from ui.console import _c, worker_color, Color
            names = ", ".join(_c(worker_color(n), n) for n in creative_display)
            print(_c(Color.ROUTE, f"🎨 Creative team: ") + names)

        if (plan.collaboration_needed or plan.preparation_workers
                or plan.creative_workers or plan.design_worker
                or plan.review_workers or plan.qa_worker):
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
