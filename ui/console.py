"""
Console UI - Colored, structured output for the AI team workflow.

Provides real-time visibility into routing decisions, worker thinking,
and inter-worker communication.
"""

import sys
from enum import Enum


class Color(Enum):
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    # Workers
    DEVELOPER = "\033[38;5;39m"   # Blue
    QA = "\033[38;5;208m"         # Orange
    ARCHITECT = "\033[38;5;141m"  # Purple
    CODE_OWNER = "\033[38;5;114m" # Green
    REVIEWER = "\033[38;5;210m"   # Pink
    # Status
    SYSTEM = "\033[38;5;245m"     # Gray
    ROUTE = "\033[38;5;220m"      # Yellow
    HANDOFF = "\033[38;5;51m"     # Cyan
    ERROR = "\033[38;5;196m"      # Red
    SUCCESS = "\033[38;5;82m"     # Bright green


WORKER_COLORS = {
    "Developer": Color.DEVELOPER,
    "QA": Color.QA,
    "Architect": Color.ARCHITECT,
    "Code Owner": Color.CODE_OWNER,
    "Reviewer": Color.REVIEWER,
    "Product Owner": Color.ROUTE,
    "Business Analyst": Color.HANDOFF,
    # Game team
    "Game Developer": Color.DEVELOPER,
    "Game QA": Color.QA,
    "Game Architect": Color.ARCHITECT,
    "Game Code Owner": Color.CODE_OWNER,
    "Game Reviewer": Color.REVIEWER,
    "Game Product Owner": Color.ROUTE,
    "Game Business Analyst": Color.HANDOFF,
    "Game Designer": Color.SUCCESS,
    "Screenwriter": Color.HANDOFF,
    "Level Designer": Color.CODE_OWNER,
    "Artist": Color.ERROR,
    "Graphical Designer": Color.DEVELOPER,
}


def _c(color: Color, text: str) -> str:
    return f"{color.value}{text}{Color.RESET.value}"


def _bold(text: str) -> str:
    return f"{Color.BOLD.value}{text}{Color.RESET.value}"


def worker_color(worker_name: str) -> Color:
    return WORKER_COLORS.get(worker_name, Color.SYSTEM)


def print_banner():
    print(_c(Color.SYSTEM, "━" * 70))
    print(_bold("🤖 Kiro AI Team - Interactive Mode"))
    print(_c(Color.SYSTEM, "Type your task or question. Type 'quit' to exit."))
    print(_c(Color.SYSTEM, "━" * 70))
    print()


def print_routing(task_type: str, primary: str, supporting: list[str], collaborate: bool,
                  preparation: list[str] | None = None,
                  designer: str | None = None,
                  reviewers: list[str] | None = None,
                  qa: str | None = None):
    """Show the routing decision."""
    print()
    print(_c(Color.ROUTE, f"📋 Task type: {task_type}"))
    if preparation:
        names = ", ".join(_c(worker_color(n), n) for n in preparation)
        print(_c(Color.ROUTE, f"📝 Preparation: ") + names)
    if designer:
        print(_c(Color.ROUTE, f"🏗️  Design: ") + _c(worker_color(designer), designer))
    color = worker_color(primary)
    print(_c(Color.ROUTE, f"🎯 Primary worker: ") + _c(color, _bold(primary)))
    if reviewers:
        names = ", ".join(_c(worker_color(n), n) for n in reviewers)
        print(_c(Color.ROUTE, f"🔍 Reviewers: ") + names)
    if supporting:
        names = ", ".join(
            _c(worker_color(n), n) for n in supporting
        )
        print(_c(Color.ROUTE, f"🤝 Supporting: ") + names)
    if qa:
        print(_c(Color.ROUTE, f"🧪 QA: ") + _c(worker_color(qa), qa))
    if collaborate:
        print(_c(Color.ROUTE, "🔄 Collaboration mode: ON"))
    print(_c(Color.SYSTEM, "─" * 70))


def print_worker_start(worker_name: str, role: str):
    """Announce a worker is starting."""
    color = worker_color(worker_name)
    icon = _worker_icon(worker_name)
    print()
    print(_c(color, f"{icon} [{worker_name}] ") + _c(Color.DIM, f"({role})"))
    print(_c(color, "   Thinking..."))


def print_worker_stream(worker_name: str, line: str):
    """Print a single line of streaming output from a worker."""
    color = worker_color(worker_name)
    prefix = _c(color, f"   │ ")
    sys.stdout.write(f"{prefix}{line}\n")
    sys.stdout.flush()


def print_worker_done(worker_name: str, success: bool, duration: float):
    """Announce a worker has finished."""
    color = worker_color(worker_name)
    icon = _worker_icon(worker_name)
    if success:
        status = _c(Color.SUCCESS, "✓ Done")
    else:
        status = _c(Color.ERROR, "✗ Failed")
    dur = f"{duration:.1f}s"
    print(_c(color, f"   └─ {icon} [{worker_name}] ") + status + _c(Color.DIM, f" ({dur})"))


def print_handoff(from_worker: str, to_worker: str):
    """Show context being passed between workers."""
    fc = worker_color(from_worker)
    tc = worker_color(to_worker)
    print()
    print(
        _c(Color.HANDOFF, "   ⤷ Passing context: ")
        + _c(fc, from_worker)
        + _c(Color.HANDOFF, " → ")
        + _c(tc, to_worker)
    )


def print_summary(results: list, total_duration: float):
    """Print final summary."""
    print()
    print(_c(Color.SYSTEM, "━" * 70))
    print(_bold("📊 Summary"))
    for r in results:
        color = worker_color(r.worker_name)
        icon = "✓" if r.success else "✗"
        print(f"   {_c(color, f'{icon} {r.worker_name}')}")
    print(_c(Color.DIM, f"   Total time: {total_duration:.1f}s"))
    print(_c(Color.SYSTEM, "━" * 70))
    print()


def _worker_icon(name: str) -> str:
    icons = {
        "Developer": "👨‍💻",
        "QA": "🔍",
        "Architect": "🏗️",
        "Code Owner": "🔐",
        "Reviewer": "📝",
        "Product Owner": "📋",
        "Business Analyst": "📊",
        # Game team
        "Game Developer": "🎮",
        "Game QA": "🧪",
        "Game Architect": "⚙️",
        "Game Code Owner": "🔐",
        "Game Reviewer": "📝",
        "Game Product Owner": "📋",
        "Game Business Analyst": "📊",
        "Game Designer": "🎲",
        "Screenwriter": "✍️",
        "Level Designer": "🗺️",
        "Artist": "🎨",
        "Graphical Designer": "🖼️",
    }
    return icons.get(name, "🤖")


def print_worker_retry(worker_name: str, attempt: int, max_retries: int, error: str):
    """Show that a worker is retrying after a failure."""
    color = worker_color(worker_name)
    icon = _worker_icon(worker_name)
    print()
    print(
        _c(Color.ERROR, f"   ⚠ Attempt {attempt}/{max_retries} failed: ")
        + _c(Color.DIM, error[:120])
    )
    print(_c(color, f"   {icon} [{worker_name}] Retrying with different approach..."))


def print_phase(phase_name: str, description: str):
    """Show a pipeline phase header."""
    print()
    print(_c(Color.SYSTEM, f"  ┌─ Phase: {phase_name}"))
    print(_c(Color.DIM, f"  │  {description}"))
    print(_c(Color.SYSTEM, f"  │"))
