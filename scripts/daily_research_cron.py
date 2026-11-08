#!/usr/bin/env /home/ubuntu/.venvs/antigravity/bin/python
"""
Daily Autonomous Deep Research Cron Runner
==========================================
Executes daily at 10:00 UTC, conducts deep research on the next
enterprise AI topic in the ontology, pushes to GitHub, and dispatches
an executive Telegram alert via @AzGem_Bot.

Author: Amz34 / Antigravity
"""

import os
import sys
import subprocess
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parent.parent
CLI_BIN = ENGINE_DIR / "deep_research.py"

def ensure_env():
    if not os.environ.get("GEMINI_API_KEY"):
        # Load fallback from .bashrc if cron ran without login shell
        bashrc_path = Path.home() / ".bashrc"
        if bashrc_path.exists():
            with open(bashrc_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "export GEMINI_API_KEY=" in line:
                        key = line.split("export GEMINI_API_KEY=")[-1].strip().strip('"').strip("'")
                        os.environ["GEMINI_API_KEY"] = key
                        break

def main():
    ensure_env()
    print("=" * 60)
    print("🚀 [CRON] Starting Daily Autonomous Deep Research Cycle...")
    cmd = [sys.executable, str(CLI_BIN), "trending", "--push"]
    res = subprocess.run(cmd, cwd=str(ENGINE_DIR))
    sys.exit(res.returncode)

if __name__ == "__main__":
    main()
