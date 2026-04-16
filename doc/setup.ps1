#Requires -Version 5.1
<#
.SYNOPSIS
    Kiro AI Team — automated Windows setup script.
.DESCRIPTION
    Run from the project root: powershell -ExecutionPolicy Bypass -File doc\setup.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Info  { param([string]$Msg) Write-Host "  $Msg" -ForegroundColor Green }
function Write-Warn  { param([string]$Msg) Write-Host "  $Msg" -ForegroundColor Yellow }
function Write-Fail  { param([string]$Msg) Write-Host "  $Msg" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "=== Kiro AI Team - Setup ===" -ForegroundColor Cyan
Write-Host ""

# -- 1. Check Python --------------------------------------------------------
Write-Host "> Checking Python..."
$pythonCmd = $null
foreach ($cmd in @("python3", "python")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -ge 3 -and $minor -ge 12) {
                $pythonCmd = $cmd
                break
            }
        }
    } catch { }
}
if (-not $pythonCmd) {
    Write-Fail "Python 3.12+ not found. Install from https://www.python.org"
}
Write-Info "Found: $(& $pythonCmd --version 2>&1) (command: $pythonCmd)"

# -- 2. Check pip -----------------------------------------------------------
Write-Host "> Checking pip..."
$pipCmd = $null
foreach ($cmd in @("pip3", "pip")) {
    try {
        $null = & $cmd --version 2>&1
        $pipCmd = $cmd
        break
    } catch { }
}
if (-not $pipCmd) {
    Write-Warn "pip not found, attempting ensurepip..."
    & $pythonCmd -m ensurepip --upgrade
    $pipCmd = "$pythonCmd -m pip"
}
Write-Info "pip found (command: $pipCmd)"

# -- 3. Check Kiro CLI ------------------------------------------------------
Write-Host "> Checking Kiro CLI..."
try {
    $kiroVer = & kiro-cli --version 2>&1
    Write-Info "kiro-cli $kiroVer"
} catch {
    Write-Fail "kiro-cli not found. Install from https://kiro.dev/cli/ then run this script again."
}

# -- 4. Verify Kiro CLI login -----------------------------------------------
Write-Host "> Checking Kiro CLI authentication..."
try {
    $whoami = & kiro-cli whoami 2>&1
    Write-Info "Logged in: $($whoami | Select-Object -First 1)"
} catch {
    Write-Warn "Not logged in. Running: kiro-cli login"
    & kiro-cli login
    try {
        $null = & kiro-cli whoami 2>&1
        Write-Info "Login successful"
    } catch {
        Write-Fail "Login failed. Run 'kiro-cli login' manually and try again."
    }
}

# -- 5. Install Python dependencies -----------------------------------------
Write-Host "> Installing Python dependencies..."
& $pipCmd install -r requirements.txt
Write-Info "Dependencies installed"

# -- 6. Create config.yaml --------------------------------------------------
Write-Host "> Setting up configuration..."
if (Test-Path "config.yaml") {
    Write-Info "config.yaml already exists - skipping"
} else {
    Copy-Item "config.yaml.example" "config.yaml"
    Write-Info "Created config.yaml from template"
    Write-Warn "Edit config.yaml to set your project path and optional Jira credentials"
}

# -- 7. Register agents (local workspace) -----------------------------------
Write-Host "> Registering agents with Kiro CLI..."
if (-not (Test-Path ".kiro\agents")) {
    New-Item -ItemType Directory -Path ".kiro\agents" -Force | Out-Null
}
Copy-Item "agents\*.json" ".kiro\agents\" -Force
Write-Info "Agents copied to .kiro\agents\"

# -- 8. Register agents in target project (if configured) -------------------
try {
    $projectPath = & $pythonCmd -c @"
import yaml, os
try:
    cfg = yaml.safe_load(open('config.yaml'))
    p = cfg.get('project', {}).get('default_path', '.')
    if p != '.' and p != os.getcwd():
        print(p)
except: pass
"@ 2>$null
} catch { $projectPath = "" }

if ($projectPath -and (Test-Path $projectPath)) {
    Write-Host "> Registering agents in target project: $projectPath"
    $targetAgents = Join-Path $projectPath ".kiro\agents"
    if (-not (Test-Path $targetAgents)) {
        New-Item -ItemType Directory -Path $targetAgents -Force | Out-Null
    }
    Copy-Item "agents\*.json" "$targetAgents\" -Force
    Write-Info "Agents also copied to $targetAgents\"
} elseif ($projectPath) {
    Write-Warn "Target project path '$projectPath' does not exist yet - agents not copied there."
}

# -- 9. Verify agents -------------------------------------------------------
Write-Host "> Verifying agent registration..."
$expectedAgents = @("architect", "business-analyst", "code-owner", "developer", "product-owner", "qa", "reviewer")
$agentList = & kiro-cli agent list 2>&1
$missing = @()
foreach ($agent in $expectedAgents) {
    if ($agentList -notmatch $agent) {
        $missing += $agent
    }
}
if ($missing.Count -eq 0) {
    Write-Info "All 7 agents registered"
} else {
    Write-Fail "Missing agents: $($missing -join ', ') - check .kiro\agents\ directory"
}

# -- 10. Verify imports ------------------------------------------------------
Write-Host "> Verifying Python imports..."
& $pythonCmd -c "from orchestrator.engine import Orchestrator; from config_loader import load_config; print('All imports OK')"

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Run the project:"
Write-Host "  $pythonCmd main.py                              # interactive mode"
Write-Host "  $pythonCmd main.py --task `"your task here`"      # direct task"
Write-Host ""
