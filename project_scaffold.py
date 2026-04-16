"""Project Scaffold - Creates structured project directories for tasks.

Every task gets its own folder under a configurable output directory with
a standard layout that mirrors the pipeline stages:

    <task-slug>/
    ├── docs/          # PO requirements, BA specs, Architect design
    ├── src/           # Developer source code
    ├── reviews/       # Reviewer and Code Owner feedback
    └── tests/         # QA test procedures and results
"""

import os
import re


def slugify(name: str, max_words: int = 4) -> str:
    """Convert a task description into a human-friendly folder name.

    Strips filler words, greetings, and common request verbs to extract
    the meaningful project name from a natural-language task description.

    Examples:
        "Hi, please create a tetris game on python" → "tetris-game-python"
        "Create a weather app with GUI"              → "weather-app-gui"
        "Write a script to parse CSV files"          → "script-parse-csv-files"
        "Fix the login bug"                          → "login-bug"
    """
    words = re.sub(r"[^a-z0-9\s]", "", name.lower()).split()
    skip = {
        # articles & conjunctions
        "a", "an", "the", "for", "to", "and", "or", "with", "that", "this",
        "of", "in", "on", "by", "from", "into", "about", "its",
        # greetings & filler
        "hi", "hey", "hello", "please", "pls", "kindly", "can", "you",
        "could", "would", "should", "lets", "let",
        # common request verbs (we want the noun, not the action)
        "create", "make", "build", "write", "develop", "implement",
        "add", "generate", "design", "setup", "set",
    }
    slug_words = [w for w in words if w not in skip][:max_words]
    return "-".join(slug_words) or "project"


def _unique_folder(base_path: str, slug: str) -> str:
    """Return a unique folder path, appending a numeric suffix on collision."""
    candidate = os.path.join(base_path, slug)
    if not os.path.exists(candidate):
        return candidate
    counter = 2
    while os.path.exists(f"{candidate}-{counter}"):
        counter += 1
    return f"{candidate}-{counter}"


def create_project_folder(base_path: str, task: str, with_subdirs: bool = True) -> dict:
    """Create a project folder for a task.

    Args:
        base_path: Parent directory (e.g. ``projects/`` or config output dir).
        task: The task description, used to derive the folder name.
        with_subdirs: When True, create ``docs/``, ``src/``, ``reviews/``,
            and ``tests/`` inside.

    Returns:
        dict with key ``root`` (always), plus ``docs``, ``src``, ``reviews``,
        and ``tests`` when *with_subdirs* is True.
    """
    slug = slugify(task)
    root = _unique_folder(base_path, slug)
    os.makedirs(root, exist_ok=True)

    paths = {"root": root}

    if with_subdirs:
        for sub in ("docs", "src", "reviews", "tests"):
            p = os.path.join(root, sub)
            os.makedirs(p, exist_ok=True)
            paths[sub] = p

    return paths


# Backward-compatible alias
def create_project_structure(base_path: str, task: str) -> dict:
    return create_project_folder(base_path, task, with_subdirs=True)
