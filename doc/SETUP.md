# Kiro AI Team — Setup Guide

## Prerequisites

| Tool | Minimum Version | Check |
|------|----------------|-------|
| Python | 3.12+ | `python3 --version` / `python --version` |
| pip | any | `pip3 --version` / `pip --version` |
| [Kiro CLI](https://kiro.dev/cli/) | latest | `kiro-cli --version` |
| Git | any | `git --version` |

## Automated Setup

Run the script for your platform from the project root:

```bash
# macOS / Linux
bash doc/setup.sh

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File doc\setup.ps1
```

The scripts check prerequisites, install dependencies, create the config file, register agents, and verify everything works.

## Manual Step-by-step Setup

### 1. Clone the repository

```bash
git clone https://github.com/YevheniL/kiro-ai-team.git
cd kiro-ai-team
```

### 2. Install Kiro CLI

Download and install from [https://kiro.dev/cli/](https://kiro.dev/cli/).

On macOS with Homebrew:

```bash
brew install kiro-cli
```

Or follow the platform-specific instructions on the Kiro CLI page.

### 3. Authenticate Kiro CLI

```bash
kiro-cli login
```

Verify you are logged in:

```bash
kiro-cli whoami
```

### 4. Ensure `~/.local/bin` is on your PATH

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 5. Install Python dependencies

```bash
pip3 install -r requirements.txt
```

### 6. Create your configuration file

```bash
cp config.yaml.example config.yaml
```

Edit `config.yaml` to set:
- `project.default_path` — path to the project you want the AI team to work on
- `project.output_dir` — folder name where task outputs are created (default: `projects`)
- `jira.*` — optional Jira integration credentials

### 7. Register agents with Kiro CLI

The agents must be registered in the directory where you run the tool:

```bash
mkdir -p .kiro/agents
cp agents/*.json .kiro/agents/
```

If you set a custom `project.default_path` in config, also register agents there:

```bash
mkdir -p /path/to/your/project/.kiro/agents
cp agents/*.json /path/to/your/project/.kiro/agents/
```

Verify they are registered:

```bash
kiro-cli agent list
```

You should see `architect`, `business-analyst`, `code-owner`, `developer`, `product-owner`, `qa`, and `reviewer` in the workspace list.

### 8. Verify everything works

```bash
python3 -c "from orchestrator.engine import Orchestrator; from config_loader import load_config; print('✅ All imports OK')"
```

## Running the Project

```bash
# Interactive mode
python3 main.py

# Direct task
python3 main.py --task "Create a weather app with GUI"

# Target a specific project
python3 main.py --project /path/to/project --task "Fix the login bug"
```

## Running Tests

```bash
python3 -m unittest discover -s tests -v
```
