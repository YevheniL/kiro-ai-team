"""
Base Worker - Abstract base for all AI workers.

Each worker wraps kiro-cli calls with role-specific prompts
and knows how to operate on external project directories.

Workers use kiro-cli custom agents under the hood:
  kiro-cli chat --no-interactive --trust-all-tools --agent <agent-name> "prompt"

Each worker has a corresponding agent JSON config in .kiro/agents/.
"""

import os
import platform
import subprocess
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ui.console import (
    print_worker_start, print_worker_stream,
    print_worker_done, print_worker_retry,
)


@dataclass
class WorkerResult:
    worker_name: str
    output: str
    success: bool = True
    duration: float = 0.0
    retries: int = 0


class BaseWorker(ABC):
    """Base class for all AI workers."""

    name: str = "base"
    agent_name: str = "base"
    role_description: str = ""

    def __init__(
        self,
        kiro_cli: str = "kiro-cli",
        project_path: str = ".",
        timeout: int = 600,
        max_retries: int = 2,
    ):
        self.kiro_cli = kiro_cli
        self.project_path = project_path
        self.timeout = timeout
        self.max_retries = max_retries

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the role-specific system prompt for this worker."""
        ...

    def execute(self, task: str, project_path: str) -> WorkerResult:
        """Execute a task with retry logic on failure."""
        prompt = self._build_prompt(task)
        print_worker_start(self.name, self.role_description)
        start = time.time()
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    # Build a retry prompt that includes the error context
                    retry_prompt = self._build_retry_prompt(task, last_error, attempt)
                    print_worker_retry(self.name, attempt, self.max_retries, str(last_error))
                    output = self._call_kiro_streaming(retry_prompt, project_path)
                else:
                    output = self._call_kiro_streaming(prompt, project_path)

                duration = time.time() - start
                print_worker_done(self.name, True, duration)
                return WorkerResult(
                    worker_name=self.name, output=output,
                    success=True, duration=duration, retries=attempt,
                )
            except Exception as e:
                last_error = e

        # All retries exhausted
        duration = time.time() - start
        print_worker_done(self.name, False, duration)
        return WorkerResult(
            worker_name=self.name,
            output=f"Error after {self.max_retries + 1} attempts: {last_error}",
            success=False, duration=duration, retries=self.max_retries,
        )

    def _build_prompt(self, task: str) -> str:
        """Combine system prompt with the task."""
        return f"{self.get_system_prompt()}\n\nTask:\n{task}"

    def _build_retry_prompt(self, task: str, error: Exception, attempt: int) -> str:
        """Build a prompt that tells the agent about the previous failure."""
        return (
            f"{self.get_system_prompt()}\n\n"
            f"Task:\n{task}\n\n"
            f"IMPORTANT: A previous attempt (#{attempt}) failed with this error:\n"
            f"  {error}\n\n"
            f"Please try a different approach to complete the task. "
            f"Avoid the approach that caused the error."
        )

    def _call_kiro_streaming(self, prompt: str, project_path: str) -> str:
        """Invoke kiro-cli and stream output line-by-line in real time.

        Uses UTF-8 encoding with error replacement to handle any character
        encoding issues cross-platform (Windows charmap, etc.).

        For long prompts on Windows, writes the prompt to a temp file in the
        project directory and tells kiro-cli to read and follow it.
        """
        resolved_path = os.path.abspath(project_path)

        # Force UTF-8 environment for kiro-cli output
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        if platform.system() == "Windows":
            env["PYTHONUTF8"] = "1"

        # Windows CreateProcessW has a ~32767 char limit for the full command line.
        # For long prompts, write to a file and pass a short reference command.
        prompt_file_path = None
        if platform.system() == "Windows" and len(prompt) > 20000:
            prompt_file_path = os.path.join(resolved_path, "_kiro_task_prompt.md")
            with open(prompt_file_path, "w", encoding="utf-8") as f:
                f.write(prompt)

            short_prompt = (
                f"Read the file '_kiro_task_prompt.md' in the current directory. "
                f"It contains your full task instructions. Follow ALL instructions "
                f"in that file completely. Do not summarize — execute the task."
            )
            cmd = self._build_command(short_prompt)
        else:
            cmd = self._build_command(prompt)

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=resolved_path,
            env=env,
            bufsize=1,
        )

        lines: list[str] = []
        try:
            for raw_line in process.stdout:
                # Decode with error handling to avoid charmap crashes
                line = raw_line.decode("utf-8", errors="replace").rstrip("\n\r")
                lines.append(line)
                print_worker_stream(self.name, line)
            process.wait(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            raise RuntimeError(f"kiro-cli timed out after {self.timeout}s")
        finally:
            # Clean up the prompt file
            if prompt_file_path and os.path.exists(prompt_file_path):
                try:
                    os.unlink(prompt_file_path)
                except OSError:
                    pass

        if process.returncode != 0:
            raise RuntimeError(f"kiro-cli exited with code {process.returncode}")

        return "\n".join(lines)

    def _build_command(self, prompt: str) -> list[str]:
        """Build the kiro-cli command. Override in subclasses if needed."""
        return [
            self.kiro_cli,
            "chat",
            "--no-interactive",
            "--trust-all-tools",
            "--agent", self.agent_name,
            prompt,
        ]
