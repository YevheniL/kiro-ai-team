"""
Game Collaboration Pipeline - Manages multi-worker game task execution.

Game development flow:
  Game PO → Game BA → Game Designer → Screenwriter → Artist → Graphical Designer
  → Level Designer → Game Architect (design) → Game Developer
  → Game Reviewer + Game Code Owner → Game Developer (fix) → Game QA

Each stage passes context forward so workers build on each other's output.
Every worker writes its deliverable as a file inside the task's project folder.

INTERACTIVE MODE: After each worker completes, the pipeline pauses and asks
the user for feedback. The user can:
  - Press Enter to continue to the next worker
  - Type feedback/answers that get appended to the next worker's context
  - Type 'skip' to skip the current phase
  - Type 'stop' to halt the pipeline entirely
"""

import sys
import time

from game_orchestrator.router import GameTaskPlan
from workers.base import WorkerResult
from ui.console import print_handoff, print_summary, print_phase


# File-save instructions appended to each worker's prompt
_GAME_SAVE_INSTRUCTIONS = {
    "game_product_owner": (
        "\n\nIMPORTANT: Save your refined requirements as a markdown file "
        "named 'docs/requirements.md' (create the docs/ directory if needed)."
    ),
    "game_business_analyst": (
        "\n\nIMPORTANT: Save your technical specification as a markdown file "
        "named 'docs/technical-spec.md' (create the docs/ directory if needed)."
    ),
    "game_architect": (
        "\n\nIMPORTANT: Save your architecture design as a markdown file "
        "named 'docs/architecture.md' (create the docs/ directory if needed)."
    ),
    "game_designer": (
        "\n\nIMPORTANT: Save your game design document as a markdown file "
        "named 'design/game-design.md' (create the design/ directory if needed)."
    ),
    "screenwriter": (
        "\n\nIMPORTANT: Save your narrative document as a markdown file "
        "named 'design/narrative.md' (create the design/ directory if needed)."
    ),
    "artist": (
        "\n\nIMPORTANT: Save your art direction document as a markdown file "
        "named 'design/art-direction.md' (create the design/ directory if needed)."
    ),
    "graphical_designer": (
        "\n\nIMPORTANT: Save your UI design document as a markdown file "
        "named 'design/ui-design.md' (create the design/ directory if needed)."
    ),
    "level_designer": (
        "\n\nIMPORTANT: Save your level design document as a markdown file "
        "named 'design/level-design.md' (create the design/ directory if needed)."
    ),
    "game_reviewer": (
        "\n\nIMPORTANT: Save your code review as a markdown file "
        "named 'reviews/code-review.md' (create the reviews/ directory if needed)."
    ),
    "game_code_owner": (
        "\n\nIMPORTANT: Save your standards review as a markdown file "
        "named 'reviews/standards-review.md' (create the reviews/ directory if needed)."
    ),
    "game_qa": (
        "\n\nIMPORTANT: Save your test plan as 'tests/test-plan.md' and your "
        "test results as 'tests/test-results.md' (create the tests/ directory if needed)."
    ),
    "game_developer": (
        "\n\nIMPORTANT: Write all source code files inside the 'src/' directory "
        "(create the src/ directory if needed)."
    ),
}


# ── Interactive checkpoint ──────────────────────────────────────────

_CHECKPOINT_BANNER = (
    "\n╔══════════════════════════════════════════════════════════════╗\n"
    "║  ✋  CHECKPOINT — {worker_name} finished                     \n"
    "╠══════════════════════════════════════════════════════════════╣\n"
    "║  Enter     → continue to next worker                        \n"
    "║  feedback  → type your notes/answers (sent to next worker)  \n"
    "║  skip      → skip remaining workers in this phase           \n"
    "║  stop      → halt the entire pipeline                       \n"
    "╚══════════════════════════════════════════════════════════════╝"
)


def _checkpoint(worker_name: str, result: WorkerResult,
                interactive: bool = True) -> tuple[str, str]:
    """Pause after a worker completes and collect user feedback.

    Returns:
        (action, feedback) where action is 'continue', 'skip', or 'stop'
        and feedback is any text the user typed (empty string if none).
    """
    if not interactive:
        return "continue", ""

    status = "✅ succeeded" if result.success else "❌ failed"
    print(f"\n{'─' * 64}")
    print(f"  {worker_name}: {status} ({result.duration:.1f}s)")
    print(f"{'─' * 64}")
    print(f"  [Enter] continue  |  [skip] skip phase  |  [stop] halt pipeline")
    print(f"  Or type your feedback / answers for the next worker:")
    print()

    lines: list[str] = []
    try:
        while True:
            line = input("  You: ").strip()
            if line == "":
                # Empty line = done with feedback, continue
                break
            if line.lower() == "skip":
                return "skip", ""
            if line.lower() == "stop":
                return "stop", ""
            lines.append(line)
            print("  (Enter another line, or press Enter on empty line to continue)")
    except (EOFError, KeyboardInterrupt):
        print("\n  [Continuing...]")
        return "continue", ""

    feedback = "\n".join(lines)
    if feedback:
        print(f"\n  📝 Feedback recorded ({len(feedback)} chars) — will be sent to next worker.\n")
    return "continue", feedback


class GameCollaborationPipeline:
    def __init__(self, workers: dict, interactive: bool = True):
        self.workers = workers
        self.interactive = interactive
        self._user_feedback: list[str] = []  # accumulated feedback from checkpoints

    @staticmethod
    def _save_hint(worker_key: str) -> str:
        return _GAME_SAVE_INSTRUCTIONS.get(worker_key, "")

    def _feedback_context(self) -> str:
        """Return accumulated user feedback as context string, then clear it."""
        if not self._user_feedback:
            return ""
        ctx = (
            "\n\n=== FEEDBACK FROM THE GAME OWNER (MANDATORY — address these) ===\n"
            + "\n".join(self._user_feedback)
            + "\n=== END FEEDBACK ===\n"
        )
        self._user_feedback.clear()
        return ctx

    def _do_checkpoint(self, worker_name: str, result: WorkerResult) -> str:
        """Run checkpoint and collect feedback. Returns action."""
        action, feedback = _checkpoint(worker_name, result, self.interactive)
        if feedback:
            self._user_feedback.append(feedback)
        return action

    def run(self, plan: GameTaskPlan, task: str, paths: dict) -> list[WorkerResult]:
        """Run the full game development pipeline with interactive checkpoints."""
        results: list[WorkerResult] = []
        start = time.time()

        # Phase 1: Preparation (Game PO, Game BA refine the task)
        refined_task = task
        if plan.preparation_workers:
            print_phase("Preparation", "Refining game requirements...")
            refined_task, prep_results = self._run_preparation(
                plan.preparation_workers, task, paths,
            )
            results.extend(prep_results)

        # Phase 2: Creative (Game Designer, Screenwriter, Artist, etc.)
        creative_context = ""
        if plan.creative_workers:
            print_phase("Creative", "Game design, narrative, art, and level design...")
            creative_context, creative_results = self._run_creative(
                plan.creative_workers, task, refined_task, paths,
            )
            results.extend(creative_results)
            if creative_context:
                refined_task = (
                    f"Requirements:\n{refined_task}\n\n"
                    f"Creative direction:\n{creative_context}\n\n"
                )

        # Phase 3: Architecture design
        if plan.design_worker:
            designer = self.workers.get(plan.design_worker)
            if designer:
                print_phase("Architecture", "Game systems architecture design...")
                prev_name = self._last_worker_name(
                    plan.creative_workers or plan.preparation_workers
                )
                if prev_name:
                    print_handoff(prev_name, designer.name)

                design_prompt = (
                    f"Original user request: {task}\n\n"
                    f"Refined requirements and creative direction:\n{refined_task}\n\n"
                    + self._feedback_context()
                    + "Please create a technical game architecture for this task. Include:\n"
                    "- Game systems and their interactions\n"
                    "- Entity/component structure\n"
                    "- Game loop and state management\n"
                    "- Asset pipeline and resource management\n"
                    "- File structure for the implementation\n\n"
                    "The game developer will implement based on your design."
                    + self._save_hint(plan.design_worker)
                )

                design_result = designer.execute(design_prompt, paths["root"])
                results.append(design_result)

                action = self._do_checkpoint(designer.name, design_result)
                if action == "stop":
                    total_duration = time.time() - start
                    print_summary(results, total_duration)
                    return results

                if design_result.success:
                    refined_task = (
                        f"{refined_task}\n\n"
                        f"Technical architecture from Game Architect:\n"
                        f"{design_result.output}\n\n"
                        f"Implement according to this design."
                    )

        # Phase 4: Primary worker executes
        print_phase("Execution", "Running primary game worker...")
        primary = self.workers.get(plan.primary_worker)
        if not primary:
            results.append(WorkerResult(
                worker_name=plan.primary_worker,
                output=f"Worker '{plan.primary_worker}' not available.",
                success=False,
            ))
            total_duration = time.time() - start
            print_summary(results, total_duration)
            return results

        prev_name = self._last_worker_name_from_plan(plan)
        if prev_name:
            print_handoff(prev_name, primary.name)

        primary_prompt = (
            refined_task
            + self._feedback_context()
            + self._save_hint(plan.primary_worker)
        )
        primary_result = primary.execute(primary_prompt, paths["root"])
        results.append(primary_result)

        action = self._do_checkpoint(primary.name, primary_result)
        if action == "stop":
            total_duration = time.time() - start
            print_summary(results, total_duration)
            return results

        if not primary_result.success:
            total_duration = time.time() - start
            print_summary(results, total_duration)
            return results

        # Phase 5: Review loop
        if plan.review_workers:
            review_comments = self._run_review(
                plan, primary, primary_result, task, results, paths,
            )

            if review_comments and plan.primary_worker in self.workers:
                print_phase("Fix", "Game Developer addressing review comments...")
                fix_prompt = (
                    f"Original task: {task}\n\n"
                    f"Your previous implementation:\n{primary_result.output}\n\n"
                    f"Review comments to address:\n{review_comments}\n\n"
                    + self._feedback_context()
                    + "Please fix ALL must-fix and should-fix comments. "
                    "For each comment, explain what you changed."
                )
                fix_result = primary.execute(fix_prompt, paths["root"])
                results.append(fix_result)

                action = self._do_checkpoint(primary.name, fix_result)
                if action == "stop":
                    total_duration = time.time() - start
                    print_summary(results, total_duration)
                    return results

        # Phase 6: Game QA
        if plan.qa_worker:
            qa = self.workers.get(plan.qa_worker)
            if qa:
                print_phase("Testing", "Game QA testing the deliverable...")
                last_dev_output = results[-1].output
                print_handoff(primary.name, qa.name)

                qa_prompt = (
                    f"Original task: {task}\n\n"
                    f"Final code/output from game developer:\n{last_dev_output}\n\n"
                    + self._feedback_context()
                    + "Please test this game deliverable thoroughly.\n"
                    "1. Write a test plan covering all gameplay mechanics\n"
                    "2. Execute the tests\n"
                    "3. Document the results with pass/fail for each test case"
                    + self._save_hint(plan.qa_worker)
                )
                qa_result = qa.execute(qa_prompt, paths["root"])
                results.append(qa_result)

        total_duration = time.time() - start
        print_summary(results, total_duration)
        return results

    def _run_preparation(
        self, prep_workers: list[str], task: str, paths: dict,
    ) -> tuple[str, list[WorkerResult]]:
        results: list[WorkerResult] = []
        refined = task
        prev_worker_name = None

        for worker_key in prep_workers:
            worker = self.workers.get(worker_key)
            if not worker:
                continue

            if prev_worker_name:
                prev_worker = self.workers.get(prev_worker_name)
                if prev_worker:
                    print_handoff(prev_worker.name, worker.name)

            prep_prompt = f"Original user request: {task}\n\n"
            if refined != task:
                prep_prompt += f"Previous refinement:\n{refined}\n\n"
            # Inject any user feedback from previous checkpoint
            prep_prompt += self._feedback_context()
            prep_prompt += (
                f"Please refine this into a clear, detailed, actionable game "
                f"development task from your perspective as {worker.name}."
                + self._save_hint(worker_key)
            )

            result = worker.execute(prep_prompt, paths["root"])
            results.append(result)

            if result.success:
                refined = result.output

            # Interactive checkpoint after each preparation worker
            action = self._do_checkpoint(worker.name, result)
            if action == "stop":
                return refined, results
            if action == "skip":
                return refined, results

            prev_worker_name = worker_key

        return refined, results

    def _run_creative(
        self, creative_workers: list[str], task: str, refined_task: str,
        paths: dict,
    ) -> tuple[str, list[WorkerResult]]:
        """Run creative workers with checkpoints after each one."""
        results: list[WorkerResult] = []
        all_creative: list[str] = []
        prev_worker_name = None

        for worker_key in creative_workers:
            worker = self.workers.get(worker_key)
            if not worker:
                continue

            if prev_worker_name:
                prev_worker = self.workers.get(prev_worker_name)
                if prev_worker:
                    print_handoff(prev_worker.name, worker.name)

            creative_prompt = (
                f"Original user request: {task}\n\n"
                f"Refined requirements:\n{refined_task}\n\n"
            )
            if all_creative:
                creative_prompt += (
                    f"Previous creative work:\n"
                    f"{'---'.join(all_creative)}\n\n"
                )
            # Inject user feedback
            creative_prompt += self._feedback_context()
            creative_prompt += (
                f"Please contribute your expertise as {worker.name} to this game project."
                + self._save_hint(worker_key)
            )

            result = worker.execute(creative_prompt, paths["root"])
            results.append(result)

            if result.success:
                all_creative.append(f"[{worker.name}]:\n{result.output}\n\n")

            # Interactive checkpoint
            action = self._do_checkpoint(worker.name, result)
            if action == "stop":
                return "\n".join(all_creative), results
            if action == "skip":
                return "\n".join(all_creative), results

            prev_worker_name = worker_key

        return "\n".join(all_creative), results

    def _run_review(
        self, plan: GameTaskPlan, primary, primary_result: WorkerResult,
        task: str, results: list[WorkerResult], paths: dict,
    ) -> str:
        print_phase("Review", "Reviewing the game implementation...")
        all_comments: list[str] = []

        for worker_key in plan.review_workers:
            worker = self.workers.get(worker_key)
            if not worker:
                continue

            print_handoff(primary.name, worker.name)

            review_prompt = (
                f"Original task: {task}\n\n"
                f"Game Developer ({primary.name}) implementation:\n"
                f"{primary_result.output}\n\n"
                + self._feedback_context()
                + f"Please review this game code from your perspective as {worker.name}.\n"
                f"Structure your feedback as a numbered list of comments "
                f"the developer must address."
                + self._save_hint(worker_key)
            )

            review_result = worker.execute(review_prompt, paths["root"])
            results.append(review_result)

            if review_result.success:
                all_comments.append(
                    f"[{worker.name}] review:\n{review_result.output}"
                )

            # Checkpoint after each reviewer
            action = self._do_checkpoint(worker.name, review_result)
            if action == "stop" or action == "skip":
                break

        return "\n\n---\n\n".join(all_comments)

    def _last_worker_name(self, worker_keys: list[str]) -> str | None:
        for key in reversed(worker_keys):
            worker = self.workers.get(key)
            if worker:
                return worker.name
        return None

    def _last_worker_name_from_plan(self, plan: GameTaskPlan) -> str | None:
        if plan.design_worker and plan.design_worker in self.workers:
            return self.workers[plan.design_worker].name
        return self._last_worker_name(
            plan.creative_workers or plan.preparation_workers
        )
