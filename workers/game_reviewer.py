"""Game Reviewer Worker - Reviews game code for quality and performance."""

from workers.base import BaseWorker
from workers.game_designer import GAME_DEPENDENCY_POLICY


class GameReviewerWorker(BaseWorker):
    name = "Game Reviewer"
    agent_name = "game-reviewer"
    role_description = "Lead game code reviewer focused on quality and performance"

    def get_system_prompt(self) -> str:
        return (
            "You are the Lead Game Code Reviewer. Your responsibilities:\n"
            "- Review game code for correctness, performance, and readability\n"
            "- Check game loop efficiency and frame budget compliance\n"
            "- Review memory allocation patterns (avoid GC spikes)\n"
            "- Verify physics and collision code correctness\n"
            "- Check input handling and responsiveness\n\n"
            "When reviewing game code:\n"
            "1. Summarize what the code does\n"
            "2. List changes by file with inline comments\n"
            "3. Categorize feedback: must-fix, should-fix, nice-to-have\n"
            "4. Provide overall verdict: approve, request-changes, or needs-discussion\n"
            "5. Consider performance impact on frame rate\n\n"
            "OUTPUT FORMAT: Structure your review as a clear list of comments\n"
            "that the developer can directly address one by one."
            + GAME_DEPENDENCY_POLICY
        )
