"""Launcher script — reads game_prompt.md and feeds it to the game orchestrator
with the full development pipeline forced (bypasses keyword-based routing)."""

import os
import sys

# Ensure we're running from the agents directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from game_orchestrator.engine import GameOrchestrator
from game_orchestrator.router import GameTaskPlan
from game_orchestrator.pipeline import GameCollaborationPipeline
from config_loader import load_config


class FullPipelineOrchestrator(GameOrchestrator):
    """Forces the full game development pipeline with interactive checkpoints."""

    def __init__(self, config: dict):
        super().__init__(config)
        # Replace pipeline with interactive version
        self.pipeline = GameCollaborationPipeline(self.workers, interactive=True)

    def execute(self, task: str) -> str:
        self.conversation_history.append({"role": "user", "content": task})

        # Force full development pipeline instead of keyword routing
        plan = GameTaskPlan(
            primary_worker="game_developer",
            preparation_workers=["game_product_owner", "game_business_analyst"],
            creative_workers=[
                "game_designer", "screenwriter", "artist",
                "graphical_designer", "level_designer",
            ],
            design_worker="game_architect",
            review_workers=["game_reviewer", "game_code_owner"],
            qa_worker="game_qa",
            collaboration_needed=True,
            task_type="development",
        )

        from project_scaffold import create_project_folder
        from ui.console import print_routing, _c, worker_color, Color

        output_base = self._resolve_output_base()
        paths = create_project_folder(output_base, task, with_subdirs=True)
        design_dir = os.path.join(paths["root"], "design")
        os.makedirs(design_dir, exist_ok=True)
        paths["design"] = design_dir
        self._ensure_agents(paths["root"])
        print(f"\n📁 Project folder: {os.path.abspath(paths['root'])}\n")

        # Display routing info
        primary_worker = self.workers.get(plan.primary_worker)
        primary_display = primary_worker.name if primary_worker else plan.primary_worker
        preparation_display = [
            self.workers[w].name for w in plan.preparation_workers if w in self.workers
        ]
        creative_display = [
            self.workers[w].name for w in plan.creative_workers if w in self.workers
        ]
        design_display = self.workers[plan.design_worker].name if plan.design_worker in self.workers else None
        review_display = [
            self.workers[w].name for w in plan.review_workers if w in self.workers
        ]
        qa_display = self.workers[plan.qa_worker].name if plan.qa_worker in self.workers else None

        print_routing(
            plan.task_type, primary_display, [],
            plan.collaboration_needed,
            preparation=preparation_display,
            designer=design_display,
            reviewers=review_display,
            qa=qa_display,
        )
        if creative_display:
            names = ", ".join(_c(worker_color(n), n) for n in creative_display)
            print(_c(Color.ROUTE, f"🎨 Creative team: ") + names)

        result = self.pipeline.run(plan, task, paths)
        response = self._format_result(plan, result)
        self.conversation_history.append({"role": "assistant", "content": response})
        return response


def main():
    # Read the full game prompt from file
    prompt_path = os.path.join(os.path.dirname(__file__), "game_prompt.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        task = f.read()

    # Load game config
    config = load_config("game_config.yaml")

    # Override project path to D:\GameProject
    config["project"]["default_path"] = r"D:\GameProject"
    config["project"]["output_dir"] = "."

    print(f"Task length: {len(task)} characters")
    print(f"Project path: {config['project']['default_path']}")
    print(f"Starting FULL game development pipeline...\n")

    orchestrator = FullPipelineOrchestrator(config)
    result = orchestrator.execute(task)
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
    print(result)


if __name__ == "__main__":
    main()
