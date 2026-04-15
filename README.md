# Kiro AI Team

A multi-agent orchestrator powered by [Kiro CLI](https://kiro.dev/cli/) that simulates a full development team. Give it a task in plain language and a team of specialized AI workers collaborates to deliver — from requirements through design, implementation, code review, and testing.

## How It Works

When you submit a task, the orchestrator routes it through a structured pipeline depending on the task type. For development tasks, the full 8-step flow is:

```
📝 Product Owner       → refines your vague request into clear user stories
📊 Business Analyst    → creates a detailed technical spec
🏗️ Architect           → designs component structure, classes, data flow
👨‍💻 Developer           → implements based on the design
📝 Reviewer            → reviews code, produces numbered comments
🔐 Code Owner          → reviews standards and dependency compliance
👨‍💻 Developer           → fixes all review comments
🔍 QA                  → tests the final deliverable
```

All output streams in real time so you can watch each worker think, hand off context, and build on each other's work.

## Workers

| Worker | Role | Tools |
|--------|------|-------|
| **Product Owner** | Refines requirements, defines acceptance criteria, decides GUI vs CLI | read, write, shell |
| **Business Analyst** | Creates technical specs, recommends open-source libraries | read, write, shell |
| **Architect** | Designs architecture, component structure, tech choices | read, write, shell |
| **Developer** | Implements features, fixes bugs, addresses review comments | read, write, shell |
| **Reviewer** | Reviews code quality, produces structured feedback | read, shell |
| **Code Owner** | Enforces standards, checks dependencies, approves/rejects | read |
| **QA** | Tests the deliverable end-to-end, writes test cases | read, write, shell |

## Policies

All workers enforce these rules:

- **Open-source first**: Always prefer free libraries and APIs with no API key. Only use paid services if there is absolutely no free alternative (e.g., Open-Meteo over OpenWeatherMap, SQLite over cloud DBs).
- **UI for apps**: When asked to create an "app" or "application", it must have a GUI (tkinter, PyQt, Kivy, web UI, etc.). CLI output is only for scripts, parsers, cron jobs, services, or daemons.

## Task Routing

The orchestrator automatically selects the right pipeline based on keywords in your task:

| Task Type | Example | Pipeline |
|-----------|---------|----------|
| **Development** | "Create a weather app" | PO → BA → Architect → Dev → Reviewer → Code Owner → Dev (fix) → QA |
| **CLI Development** | "Write a script to parse logs" | PO → BA → Architect → Dev → Reviewer → Dev (fix) → QA |
| **Architecture** | "Design the auth module" | PO → Architect → Dev |
| **Investigation** | "Investigate the legacy code" | BA → Architect → Dev |
| **PR Review** | "Review PR #123" | Reviewer → QA → Code Owner |
| **Requirements** | "Write a Jira ticket for checkout" | PO → BA |
| **Quality** | "Test the checkout flow" | QA |
| **Default** | anything else | Full development pipeline |

## Installation

### Prerequisites

- Python 3.12+
- [Kiro CLI](https://kiro.dev/cli/) installed and authenticated (`kiro-cli login`)

### Setup

```bash
# Clone the repo
git clone https://github.com/YevheniL/kiro-ai-team.git
cd kiro-ai-team

# Install dependencies
pip install -r requirements.txt

# Copy config and edit your settings
cp config.yaml.example config.yaml

# Register the agents with kiro-cli
mkdir -p .kiro/agents
cp agents/*.json .kiro/agents/

# Verify agents are registered
kiro-cli agent list
```

## Usage

```bash
# Interactive mode — chat with the team
python main.py

# Pass a task directly
python main.py --task "Create a weather app with GUI"

# Target a specific project directory
python main.py --project /path/to/your/project --task "Fix the login bug"
```

### Examples

```bash
# Full dev pipeline: PO → BA → Architect → Dev → Review → Fix → QA
python main.py --task "Create a todo app with categories and due dates"

# Architecture review
python main.py --task "Design the architecture for a notification system"

# Code review
python main.py --task "Review PR #42"

# Quick script (no GUI)
python main.py --task "Write a script to parse CSV files and generate reports"
```

## Configuration

`config.yaml` settings:

```yaml
kiro:
  cli_path: "kiro-cli"       # Path to kiro-cli binary
  default_model: "auto"

project:
  default_path: "."           # Default project directory

jira:                          # Optional Jira integration (placeholders)
  base_url: "https://your-company.atlassian.net"
  api_token: "YOUR_TOKEN"

workers:                       # Enable/disable individual workers
  developer:
    enabled: true
  qa:
    enabled: true
  # ... etc
```

## Project Structure

```
kiro-ai-team/
├── main.py                    # Entry point (CLI + interactive)
├── config_loader.py           # YAML config with fallbacks
├── config.yaml.example        # Config template
├── requirements.txt           # Python dependencies (pyyaml)
├── orchestrator/
│   ├── engine.py              # Routes tasks, coordinates workers
│   ├── router.py              # Keyword-based task routing
│   └── pipeline.py            # 8-step collaboration pipeline
├── workers/
│   ├── base.py                # Base worker: streaming, retry, kiro-cli integration
│   ├── product_owner.py       # Requirement refinement
│   ├── business_analyst.py    # Technical specs
│   ├── architect.py           # System design
│   ├── developer.py           # Implementation
│   ├── reviewer.py            # Code review
│   ├── code_owner.py          # Standards enforcement
│   └── qa.py                  # Testing
├── agents/                    # Kiro CLI custom agent JSON configs
│   ├── product-owner.json
│   ├── business-analyst.json
│   ├── architect.json
│   ├── developer.json
│   ├── reviewer.json
│   ├── code-owner.json
│   └── qa.json
├── ui/
│   └── console.py             # Colored real-time output
└── tests/                     # 52 unit tests
    ├── test_agents.py
    ├── test_config.py
    ├── test_pipeline.py
    ├── test_router.py
    └── test_workers.py
```

## Running Tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT
