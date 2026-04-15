"""Configuration loader for Kiro AI Team."""

import os
import yaml


def load_config(path: str = "config.yaml") -> dict:
    """Load configuration from YAML file with fallback to example."""
    if not os.path.exists(path):
        example_path = f"{path}.example"
        if os.path.exists(example_path):
            print(f"⚠️  No {path} found. Using {example_path} as template.")
            print(f"   Copy it to {path} and fill in your settings.\n")
            path = example_path
        else:
            return _default_config()

    with open(path, "r") as f:
        return yaml.safe_load(f)


def _default_config() -> dict:
    return {
        "kiro": {"cli_path": "kiro-cli", "default_model": "auto"},
        "project": {"default_path": "."},
        "jira": {},
        "workers": {
            "developer": {"enabled": True},
            "qa": {"enabled": True},
            "architect": {"enabled": True},
            "code_owner": {"enabled": True},
            "reviewer": {"enabled": True},
        },
    }
