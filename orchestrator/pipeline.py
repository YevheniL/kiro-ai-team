"""
Collaboration Pipeline - Manages multi-worker task execution.

Development flow:
  PO → BA → Architect (design) → Developer → Reviewer → Code Owner → Developer (fix) → QA

Each stage passes context forward so workers build on each other's output.
"""

import time

from orchestrator.router import TaskPlan
from workers.base import WorkerResult
from ui.console import print_handoff, print_summary, print_phase


class CollaborationPipeline:
    def __init__(self, workers: dict):
        self.workers = workers

    def run(self, plan: TaskPlan, task: str) -> list[WorkerResult]:
        """Run the full pipeline with review loop for development tasks."""
        results: list[WorkerResult] = []
        start = time.time()

        # Phase 1: Preparation (PO, BA refine the task)
        refined_task = task
        if plan.preparation_workers:
            print_phase("Preparation", "Refining task requirements...")
            refined_task, prep_results = self._run_preparation(
                plan.preparation_workers, task,
            )
            results.extend(prep_results)

        # Phase 2: Design (Architect creates design based on requirements)
        if plan.design_worker:
            designer = self.workers.get(plan.design_worker)
            if designer:
                print_phase("Design", "Architect creating technical design...")
                if plan.preparation_workers:
                    last_prep = plan.preparation_workers[-1]
                    last_prep_worker = self.workers.get(last_prep)
                    if last_prep_worker:
                        print_handoff(last_prep_worker.name, designer.name)

                design_prompt = (
                    f"Original user request: {task}\n\n"
                    f"Refined requirements:\n{refined_task}\n\n"
                    f"Please create a technical design for this task. Include:\n"
                    f"- Component/module structure\n"
                    f"- Key classes, interfaces, and their responsibilities\n"
                    f"- Data flow and interactions\n"
                    f"- Technology choices and libraries to use\n"
                    f"- File structure for the implementation\n\n"
                    f"The developer will implement based on your design."
                )

                design_result = designer.execute(design_prompt, designer.project_path)
                results.append(design_result)

                if design_result.success:
                    # Enrich the task with the design for the developer
                    refined_task = (
                        f"Requirements:\n{refined_task}\n\n"
                        f"Technical design from Architect:\n{design_result.output}\n\n"
                        f"Implement according to this design."
                    )

        # Phase 3: Primary worker executes the refined task
        print_phase("Execution", "Running primary worker...")
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

        if refined_task != task:
            # Show handoff from last phase worker to primary
            if plan.design_worker and plan.design_worker in self.workers:
                print_handoff(self.workers[plan.design_worker].name, primary.name)
            elif plan.preparation_workers:
                last_prep = plan.preparation_workers[-1]
                last_prep_worker = self.workers.get(last_prep)
                if last_prep_worker:
                    print_handoff(last_prep_worker.name, primary.name)

        primary_result = primary.execute(refined_task, primary.project_path)
        results.append(primary_result)

        if not primary_result.success:
            total_duration = time.time() - start
            print_summary(results, total_duration)
            return results

        # Phase 3: Review loop (for development tasks)
        # Reviewer and Code Owner review, then Developer fixes comments
        if plan.review_workers:
            review_comments = self._run_review(
                plan, primary, primary_result, task, results,
            )

            # Phase 4: Developer fixes review comments
            if review_comments and plan.primary_worker in self.workers:
                print_phase("Fix", "Developer addressing review comments...")
                fix_result = self._run_fix(
                    primary, task, primary_result.output, review_comments,
                )
                results.append(fix_result)

        # Phase 5: QA tests the final result (always last)
        if plan.qa_worker:
            qa = self.workers.get(plan.qa_worker)
            if qa:
                print_phase("Testing", "QA testing the deliverable...")
                last_dev_output = results[-1].output
                print_handoff(primary.name, qa.name)

                qa_prompt = (
                    f"Original task: {task}\n\n"
                    f"Final code/output from developer:\n{last_dev_output}\n\n"
                    f"Please test this deliverable thoroughly."
                )
                qa_result = qa.execute(qa_prompt, qa.project_path)
                results.append(qa_result)

        total_duration = time.time() - start
        print_summary(results, total_duration)
        return results

    def _run_preparation(
        self, prep_workers: list[str], task: str,
    ) -> tuple[str, list[WorkerResult]]:
        """Run preparation workers to refine the task."""
        results: list[WorkerResult] = []
        refined = task
        prev_worker_name = None

        for worker_name in prep_workers:
            worker = self.workers.get(worker_name)
            if not worker:
                continue

            if prev_worker_name:
                prev_worker = self.workers.get(prev_worker_name)
                if prev_worker:
                    print_handoff(prev_worker.name, worker.name)

            prep_prompt = f"Original user request: {task}\n\n"
            if refined != task:
                prep_prompt += f"Previous refinement:\n{refined}\n\n"
            prep_prompt += (
                f"Please refine this into a clear, detailed, actionable task "
                f"from your perspective as {worker.name}."
            )

            result = worker.execute(prep_prompt, worker.project_path)
            results.append(result)

            if result.success:
                refined = result.output

            prev_worker_name = worker_name

        return refined, results

    def _run_review(
        self, plan: TaskPlan, primary, primary_result: WorkerResult,
        task: str, results: list[WorkerResult],
    ) -> str:
        """Run review workers and collect their comments."""
        print_phase("Review", "Reviewing the implementation...")
        all_comments: list[str] = []

        for worker_name in plan.review_workers:
            worker = self.workers.get(worker_name)
            if not worker:
                continue

            print_handoff(primary.name, worker.name)

            review_prompt = (
                f"Original task: {task}\n\n"
                f"Developer ({primary.name}) implementation:\n"
                f"{primary_result.output}\n\n"
                f"Please review this code from your perspective as {worker.name}.\n"
                f"Structure your feedback as a numbered list of comments "
                f"the developer must address."
            )

            review_result = worker.execute(review_prompt, worker.project_path)
            results.append(review_result)

            if review_result.success:
                all_comments.append(
                    f"[{worker.name}] review:\n{review_result.output}"
                )

        return "\n\n---\n\n".join(all_comments)

    def _run_fix(
        self, primary, task: str, original_output: str, review_comments: str,
    ) -> WorkerResult:
        """Have the developer fix review comments."""
        print_handoff("Reviewer", primary.name)

        fix_prompt = (
            f"Original task: {task}\n\n"
            f"Your previous implementation:\n{original_output}\n\n"
            f"Review comments to address:\n{review_comments}\n\n"
            f"Please fix ALL must-fix and should-fix comments. "
            f"For each comment, explain what you changed."
        )

        return primary.execute(fix_prompt, primary.project_path)
