#!/usr/bin/env /home/ubuntu/.venvs/antigravity/bin/python
"""
Daily Autonomous Deep Research Cron Runner
==========================================
Executes daily at 10:00 UTC, conducts deep research on the next
enterprise AI topic in the ontology, pushes to GitHub, and dispatches
an executive Telegram alert via @AzGem_Bot.

Author: Amz34 / Antigravity
"""

import sys
import subprocess
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parent.parent
CLI_BIN = ENGINE_DIR / "deep_research.py"

def main():
    print("=" * 60)
    print("🚀 [CRON] Starting Daily Autonomous Deep Research Cycle...")
    cmd = [sys.executable, str(CLI_BIN), "trending", "--push"]
    res = subprocess.run(cmd, cwd=str(ENGINE_DIR))
    sys.exit(res.returncode)

if __name__ == "__main__":
    main()
