"""Add PowerShell shell policy to all agent JSON configs."""
import json
import os
import glob
import shutil

SHELL_INSTRUCTION = (
    "\n\nSHELL POLICY (MANDATORY):\n"
    "- You are running on Windows with PowerShell.\n"
    "- NEVER use cmd.exe syntax. No 'if not exist', no bare 'mkdir', no '&&'.\n"
    "- Use PowerShell commands: New-Item -ItemType Directory -Force -Path, "
    "Test-Path, Copy-Item, Remove-Item, Get-Content, Set-Content.\n"
    "- Use semicolons (;) to chain commands, not '&&'.\n"
    "- Always use forward slashes or properly escaped backslashes in paths."
)

agents_dir = os.path.join(os.path.dirname(__file__), "agents")
kiro_dir = os.path.join(os.path.dirname(__file__), ".kiro", "agents")

count = 0
for path in sorted(glob.glob(os.path.join(agents_dir, "*.json"))):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "SHELL POLICY" not in data.get("prompt", ""):
        data["prompt"] = data["prompt"] + SHELL_INSTRUCTION
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Also update .kiro/agents copy
        kiro_path = os.path.join(kiro_dir, os.path.basename(path))
        with open(kiro_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        count += 1
        print(f"  Updated: {os.path.basename(path)}")

print(f"\nTotal updated: {count} agents")
