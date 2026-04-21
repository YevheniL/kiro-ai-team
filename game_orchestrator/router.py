"""
Game Task Router - Analyzes game tasks and determines which workers to involve.

Game development pipeline:
  Game PO → Game BA → Game Designer → Screenwriter → Artist → Graphical Designer
  → Level Designer → Game Architect (design) → Game Developer
  → Game Reviewer + Game Code Owner → Game Developer (fix) → Game QA
"""

import re
from dataclasses import dataclass, field


@dataclass
class GameTaskPlan:
    primary_worker: str
    supporting_workers: list[str] = field(default_factory=list)
    preparation_workers: list[str] = field(default_factory=list)
    creative_workers: list[str] = field(default_factory=list)
    design_worker: str | None = None
    review_workers: list[str] = field(default_factory=list)
    qa_worker: str | None = None
    collaboration_needed: bool = False
    task_type: str = "general"


# Order matters: more specific rules first, broad catch-all rules last.
GAME_ROUTING_RULES = [
    {
        "patterns": [r"review.*code", r"code.?review", r"\bpr\b", r"pull.?request"],
        "primary": "game_reviewer",
        "supporting": ["game_qa", "game_code_owner"],
        "task_type": "code-review",
    },
    {
        "patterns": [r"story", r"narrative", r"dialogue", r"lore", r"cutscene", r"script"],
        "primary": "screenwriter",
        "supporting": ["game_designer"],
        "preparation": ["game_product_owner"],
        "task_type": "narrative",
    },
    {
        "patterns": [r"level\s*design", r"\bmap\b", r"dungeon", r"world\s*map", r"encounter"],
        "primary": "level_designer",
        "supporting": ["game_designer", "artist"],
        "preparation": ["game_product_owner"],
        "task_type": "level-design",
    },
    {
        "patterns": [r"\bart\b", r"sprite", r"character\s*design", r"animation", r"tileset", r"visual\s*style"],
        "primary": "artist",
        "supporting": ["graphical_designer", "game_designer"],
        "preparation": ["game_product_owner"],
        "task_type": "art",
    },
    {
        "patterns": [r"\bui\b", r"\bux\b", r"\bhud\b", r"menu", r"interface", r"inventory\s*screen"],
        "primary": "graphical_designer",
        "supporting": ["artist", "game_designer"],
        "preparation": ["game_product_owner"],
        "task_type": "ui-design",
    },
    {
        "patterns": [r"game\s*design", r"mechanic", r"gameplay", r"balance", r"\bgdd\b", r"progression"],
        "primary": "game_designer",
        "supporting": ["level_designer", "screenwriter"],
        "preparation": ["game_product_owner"],
        "task_type": "game-design",
    },
    {
        "patterns": [r"test", r"quality", r"find.*bug", r"report.*bug", r"regression", r"playtest"],
        "primary": "game_qa",
        "collaborate": False,
        "task_type": "quality",
    },
    {
        "patterns": [r"architect", r"engine", r"system\s*design", r"\becs\b", r"render"],
        "primary": "game_architect",
        "supporting": ["game_developer"],
        "preparation": ["game_product_owner"],
        "task_type": "architecture",
    },
    {
        "patterns": [
            r"implement", r"develop", r"create.*game", r"build.*game",
            r"make.*game", r"fix.*bug", r"write.*code", r"\bcreate\b",
            r"\bbuild\b", r"\bmake\b",
        ],
        "primary": "game_developer",
        "preparation": ["game_product_owner", "game_business_analyst"],
        "creative": ["game_designer", "screenwriter", "artist", "graphical_designer", "level_designer"],
        "design": "game_architect",
        "review": ["game_reviewer", "game_code_owner"],
        "qa": "game_qa",
        "task_type": "development",
    },
]


class GameTaskRouter:
    def route(self, task: str) -> GameTaskPlan:
        """Analyze task text and return a game-specific routing plan."""
        task_lower = task.lower()

        for rule in GAME_ROUTING_RULES:
            for pattern in rule["patterns"]:
                if re.search(pattern, task_lower):
                    return GameTaskPlan(
                        primary_worker=rule["primary"],
                        supporting_workers=rule.get("supporting", []),
                        preparation_workers=rule.get("preparation", []),
                        creative_workers=rule.get("creative", []),
                        design_worker=rule.get("design"),
                        review_workers=rule.get("review", []),
                        qa_worker=rule.get("qa"),
                        collaboration_needed=rule.get("collaborate", True),
                        task_type=rule["task_type"],
                    )

        # Default: full game development pipeline
        return GameTaskPlan(
            primary_worker="game_developer",
            preparation_workers=["game_product_owner", "game_business_analyst"],
            creative_workers=["game_designer", "screenwriter", "artist",
                              "graphical_designer", "level_designer"],
            design_worker="game_architect",
            review_workers=["game_reviewer", "game_code_owner"],
            qa_worker="game_qa",
            collaboration_needed=True,
            task_type="general",
        )
