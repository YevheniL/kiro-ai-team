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

### Task Output Structure

Each task gets its own project folder under `projects/` with a clean, human-readable name derived from your task description. The folder layout mirrors the pipeline stages:

```
projects/
└── weather-app-gui/
    ├── .kiro/agents/          # Agent configs (auto-copied)
    ├── docs/
    │   ├── requirements.md    # Product Owner output
    │   ├── technical-spec.md  # Business Analyst output
    │   └── architecture.md    # Architect output
    ├── src/                   # Developer source code
    ├── reviews/
    │   ├── code-review.md     # Reviewer feedback
    │   └── standards-review.md # Code Owner feedback
    └── tests/
        ├── test-plan.md       # QA test procedures
        └── test-results.md    # QA test results
```

Duplicate task names automatically get a numeric suffix (`weather-app-gui-2`, etc.).

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

### Automated Setup

```bash
# macOS / Linux
git clone https://github.com/YevheniL/kiro-ai-team.git
cd kiro-ai-team
bash doc/setup.sh

# Windows (PowerShell)
git clone https://github.com/YevheniL/kiro-ai-team.git
cd kiro-ai-team
powershell -ExecutionPolicy Bypass -File doc\setup.ps1
```

The setup scripts check prerequisites, install Kiro CLI auth, install Python dependencies, create the config file, register agents, and verify everything works.

### Manual Setup

See [doc/SETUP.md](doc/SETUP.md) for detailed step-by-step instructions.

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
  default_path: "."           # Base directory (falls back to cwd if invalid)
  output_dir: "projects"      # Each task creates a subfolder here

jira:                          # Optional Jira integration
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
├── project_scaffold.py        # Dynamic project folder creation
├── config.yaml.example        # Config template
├── requirements.txt           # Python dependencies
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
├── doc/
│   ├── SETUP.md               # Detailed setup guide
│   ├── setup.sh               # macOS/Linux setup script
│   └── setup.ps1              # Windows setup script
├── ui/
│   └── console.py             # Colored real-time output
├── tests/                     # Unit tests
└── projects/                  # Task output (gitignored, created at runtime)
```

## Running Tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT
