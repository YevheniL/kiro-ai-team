# Kiro AI Team

A set of AI workers powered by Kiro CLI that collaborate to handle Android development workflows.

## Workers

| Worker | Role |
|--------|------|
| **Developer** | Implements features, fixes bugs, writes code |
| **QA** | Reviews code quality, finds bugs, suggests tests |
| **Architect** | Designs architecture, evaluates proposals, reviews patterns |
| **Code Owner** | Reviews changes in owned modules, approves/rejects PRs |
| **Reviewer** | Main PR reviewer, coordinates review process |

## Usage

```bash
# Start the interactive session
python main.py

# Or pass a task directly
python main.py --task "Review PR #123 in /path/to/android-project"

# Target a specific project directory
python main.py --project /path/to/android-repo
```

## Configuration

Copy `config.yaml.example` to `config.yaml` and fill in your settings:

- Jira credentials and project keys
- Default project paths
- Kiro CLI path (if not on PATH)

## Architecture

```
User → Orchestrator → Worker(s) → Kiro CLI → Results
                ↕
         Workers collaborate
         (Developer ↔ QA ↔ Architect)
```

The orchestrator analyzes your request, selects the right worker(s), and manages
their collaboration. Workers share context through a conversation pipeline.
