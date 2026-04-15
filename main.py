"""
Kiro AI Team - Main entry point.

Single interface to interact with a team of AI workers
that collaborate on Android development tasks.
"""

import argparse
import sys

from orchestrator.engine import Orchestrator
from config_loader import load_config


def main():
    parser = argparse.ArgumentParser(description="Kiro AI Team - AI-powered development assistants")
    parser.add_argument("--task", type=str, help="Task description to execute directly")
    parser.add_argument("--project", type=str, help="Path to the project directory")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.config)

    if args.project:
        config["project"]["default_path"] = args.project

    orchestrator = Orchestrator(config)

    if args.task:
        result = orchestrator.execute(args.task)
        print(result)
    else:
        run_interactive(orchestrator)


def run_interactive(orchestrator: "Orchestrator"):
    """Run interactive chat session with the AI team."""
    from ui.console import print_banner
    print_banner()

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
