#!/usr/bin/env bash
#
# Kiro AI Team — automated Mac/Linux setup script
# Run from the project root: bash doc/setup.sh
#

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}✔ $1${NC}"; }
warn()  { echo -e "${YELLOW}⚠ $1${NC}"; }
fail()  { echo -e "${RED}✖ $1${NC}"; exit 1; }

echo ""
echo "=== Kiro AI Team — Setup ==="
echo ""

# ── 1. Check Python ──────────────────────────────────────────────
echo "→ Checking Python..."
if ! command -v python3 &>/dev/null; then
  fail "python3 not found. Install Python 3.12+ from https://www.python.org"
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 12 ]; }; then
  fail "Python 3.12+ required (found $PY_VERSION)"
fi
info "Python $PY_VERSION"

# ── 2. Check pip ─────────────────────────────────────────────────
echo "→ Checking pip..."
if ! command -v pip3 &>/dev/null; then
  fail "pip3 not found. Install it with: python3 -m ensurepip --upgrade"
fi
info "pip3 found"

# ── 3. Check Kiro CLI ───────────────────────────────────────────
echo "→ Checking Kiro CLI..."
if ! command -v kiro-cli &>/dev/null; then
  fail "kiro-cli not found. Install from https://kiro.dev/cli/ then run this script again."
fi
info "kiro-cli $(kiro-cli --version 2>/dev/null || echo '(version unknown)')"

# ── 4. Verify Kiro CLI login ────────────────────────────────────
echo "→ Checking Kiro CLI authentication..."
if kiro-cli whoami &>/dev/null; then
  info "Logged in: $(kiro-cli whoami 2>/dev/null | head -1)"
else
  warn "Not logged in. Running: kiro-cli login"
  kiro-cli login
  if kiro-cli whoami &>/dev/null; then
    info "Login successful"
  else
    fail "Login failed. Run 'kiro-cli login' manually and try again."
  fi
fi

# ── 5. PATH setup ───────────────────────────────────────────────
echo "→ Ensuring ~/.local/bin is on PATH..."
if ! echo "$PATH" | tr ':' '\n' | grep -qx "$HOME/.local/bin"; then
  if [ -f "$HOME/.bashrc" ] && grep -q 'HOME/.local/bin' "$HOME/.bashrc"; then
    warn "Already in ~/.bashrc but not active in this shell. Run: source ~/.bashrc"
  else
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    export PATH="$HOME/.local/bin:$PATH"
    info "Added to ~/.bashrc and exported"
  fi
else
  info "~/.local/bin already on PATH"
fi

# ── 6. Install Python dependencies ──────────────────────────────
echo "→ Installing Python dependencies..."
pip3 install -r requirements.txt
info "Dependencies installed"

# ── 7. Create config.yaml ───────────────────────────────────────
echo "→ Setting up configuration..."
if [ -f config.yaml ]; then
  info "config.yaml already exists — skipping"
else
  cp config.yaml.example config.yaml
  info "Created config.yaml from template"
  warn "Edit config.yaml to set your project path and optional Jira credentials"
fi

# ── 8. Register agents (local workspace) ────────────────────────
echo "→ Registering agents with Kiro CLI..."
mkdir -p .kiro/agents
cp agents/*.json .kiro/agents/
info "Agents copied to .kiro/agents/"

# ── 9. Register agents in target project (if configured) ────────
PROJECT_PATH=$(python3 -c "
import yaml, os
try:
    cfg = yaml.safe_load(open('config.yaml'))
    p = cfg.get('project', {}).get('default_path', '.')
    if p != '.' and p != os.getcwd():
        print(p)
except: pass
" 2>/dev/null || true)

if [ -n "$PROJECT_PATH" ] && [ -d "$PROJECT_PATH" ]; then
  echo "→ Registering agents in target project: $PROJECT_PATH"
  mkdir -p "$PROJECT_PATH/.kiro/agents"
  cp agents/*.json "$PROJECT_PATH/.kiro/agents/"
  info "Agents also copied to $PROJECT_PATH/.kiro/agents/"
elif [ -n "$PROJECT_PATH" ]; then
  warn "Target project path '$PROJECT_PATH' does not exist yet — agents not copied there."
  warn "After creating it, run: mkdir -p $PROJECT_PATH/.kiro/agents && cp agents/*.json $PROJECT_PATH/.kiro/agents/"
fi

# ── 10. Verify agents ───────────────────────────────────────────
echo "→ Verifying agent registration..."
EXPECTED_AGENTS="architect business-analyst code-owner developer product-owner qa reviewer"
AGENT_LIST=$(kiro-cli agent list 2>&1 || true)
MISSING=""
for agent in $EXPECTED_AGENTS; do
  if ! echo "$AGENT_LIST" | grep -q "  $agent "; then
    MISSING="$MISSING $agent"
  fi
done

if [ -z "$MISSING" ]; then
  info "All 7 agents registered"
else
  fail "Missing agents:$MISSING — check .kiro/agents/ directory"
fi

# ── 11. Verify imports ──────────────────────────────────────────
echo "→ Verifying Python imports..."
python3 -c "from orchestrator.engine import Orchestrator; from config_loader import load_config; print('✅ All imports OK')"

echo ""
echo "=== Setup complete ==="
echo ""
echo "Run the project:"
echo "  python3 main.py                              # interactive mode"
echo "  python3 main.py --task \"your task here\"       # direct task"
echo ""
