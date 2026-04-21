"""
Kiro Game AI Team - Main entry point.

Single interface to interact with a team of AI workers
that collaborate on game development tasks.
"""

import argparse
import sys

from game_orchestrator.engine import GameOrchestrator
from config_loader import load_config


def main():
    parser = argparse.ArgumentParser(
        description="Kiro Game AI Team - AI-powered game development assistants"
    )
    parser.add_argument("--task", type=str, help="Task description to execute directly")
    parser.add_argument("--project", type=str, help="Path to the project directory")
    parser.add_argument("--config", type=str, default="game_config.yaml",
                        help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.config)

    if args.project:
        config["project"]["default_path"] = args.project

    orchestrator = GameOrchestrator(config)

    if args.task:
        result = orchestrator.execute(args.task)
        print(result)
    else:
        run_interactive(orchestrator)


def run_interactive(orchestrator: "GameOrchestrator"):
    """Run interactive chat session with the game AI team."""
    from ui.console import _c, _bold, Color
    print(_c(Color.SYSTEM, "━" * 70))
    print(_bold("🎮 Kiro Game AI Team - Interactive Mode"))
    print(_c(Color.SYSTEM, "Type your game task or question. Type 'quit' to exit."))
    print(_c(Color.SYSTEM, "━" * 70))
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Bye!")
            break

        result = orchestrator.execute(user_input)
        print(f"\n{result}\n")


if __name__ == "__main__":
    main()
