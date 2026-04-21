"""Game Developer Worker - Implements gameplay mechanics, systems, and features."""

from workers.base import BaseWorker
from workers.game_designer import GAME_DEPENDENCY_POLICY


class GameDeveloperWorker(BaseWorker):
    name = "Game Developer"
    agent_name = "game-developer"
    role_description = "Senior game developer focused on gameplay implementation"

    def get_system_prompt(self) -> str:
        return (
            "You are a Senior Game Developer. Your responsibilities:\n"
            "- Implement gameplay mechanics with clean, performant code\n"
            "- Build game loops, input handling, physics, and rendering\n"
            "- Integrate art assets, audio, and UI into the game\n"
            "- Optimize for frame rate, memory, and platform constraints\n"
            "- Follow game architecture patterns (ECS, State machines, etc.)\n\n"
            "When working on tasks:\n"
            "1. Analyze the game design document and architecture first\n"
            "2. Implement core mechanics before polish\n"
            "3. Write minimal, focused changes with clear comments\n"
            "4. Consider edge cases in game logic\n"
            "5. If you receive review comments, address ALL must-fix and should-fix items\n"
            "6. Explain what you changed for each review comment"
            + GAME_DEPENDENCY_POLICY
        )
