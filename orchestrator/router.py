"""
Task Router - Analyzes tasks and determines which workers to involve.

Development pipeline:
  PO → BA → Architect (design) → Developer → Reviewer + Code Owner → Developer (fix) → QA
"""

import re
from dataclasses import dataclass, field


@dataclass
class TaskPlan:
    primary_worker: str
    supporting_workers: list[str] = field(default_factory=list)
    preparation_workers: list[str] = field(default_factory=list)
    design_worker: str | None = None
    review_workers: list[str] = field(default_factory=list)
    qa_worker: str | None = None
    collaboration_needed: bool = False
    task_type: str = "general"


# Order matters: more specific rules first, broad catch-all rules last.
ROUTING_RULES = [
    {
        "patterns": [r"\bpr\b", r"pull.?request", r"review.*code", r"code.?review"],
        "primary": "reviewer",
        "supporting": ["qa", "code_owner"],
        "task_type": "pr-review",
    },
    {
        "patterns": [r"jira", r"ticket", r"\bstory\b", r"\brequirement", r"\bspec\b"],
        "primary": "product_owner",
        "supporting": ["business_analyst"],
        "task_type": "requirements",
    },
    {
        "patterns": [r"test", r"quality", r"find.*bug", r"report.*bug", r"regression", r"coverage"],
        "primary": "qa",
        "collaborate": False,
        "task_type": "quality",
    },
    {
        "patterns": [r"legacy", r"investigate", r"understand", r"explore"],
        "primary": "architect",
        "supporting": ["developer"],
        "preparation": ["business_analyst"],
        "task_type": "investigation",
    },
    {
        "patterns": [r"architect", r"design", r"proposal", r"structure", r"pattern"],
        "primary": "architect",
        "supporting": ["developer"],
        "preparation": ["product_owner"],
        "task_type": "architecture",
    },
    {
        "patterns": [
            r"implement", r"develop", r"create.*feature", r"add.*feature",
            r"fix.*bug", r"write.*code", r"\bcreate\b", r"\bbuild\b", r"\bmake\b",
        ],
        "primary": "developer",
        "preparation": ["product_owner", "business_analyst"],
        "design": "architect",
        "review": ["reviewer", "code_owner"],
        "qa": "qa",
        "task_type": "development",
    },
    {
        "patterns": [r"\bscript\b", r"\bparser\b", r"\bcron\b", r"\bservice\b", r"\bdaemon\b"],
        "primary": "developer",
        "preparation": ["product_owner", "business_analyst"],
        "design": "architect",
        "review": ["reviewer"],
        "qa": "qa",
        "task_type": "cli-development",
    },
]


class TaskRouter:
    def route(self, task: str) -> TaskPlan:
        """Analyze task text and return a routing plan."""
        task_lower = task.lower()

        for rule in ROUTING_RULES:
            for pattern in rule["patterns"]:
                if re.search(pattern, task_lower):
                    return TaskPlan(
                        primary_worker=rule["primary"],
                        supporting_workers=rule.get("supporting", []),
                        preparation_workers=rule.get("preparation", []),
                        design_worker=rule.get("design"),
                        review_workers=rule.get("review", []),
                        qa_worker=rule.get("qa"),
                        collaboration_needed=rule.get("collaborate", True),
                        task_type=rule["task_type"],
                    )

        # Default: full development pipeline
        return TaskPlan(
            primary_worker="developer",
            preparation_workers=["product_owner", "business_analyst"],
            design_worker="architect",
            review_workers=["reviewer", "code_owner"],
            qa_worker="qa",
            collaboration_needed=True,
            task_type="general",
        )
