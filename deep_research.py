#!/usr/bin/env /home/ubuntu/.venvs/antigravity/bin/python
"""
Autonomous Deep Research Engine CLI
====================================
Command-line interface for autonomous multi-angle technical research,
evidence synthesis, and whitepaper compilation.

Author: Amz34 / Antigravity
"""

import os
import sys
import argparse
import random
import subprocess
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_DIR))

from core.engine import DeepResearchEngine, REPORTS_DIR

TRENDING_ONTOLOGY = [
    "Speculative Tool Calling & Typed Decision Layers in Autonomous Agent Swarms",
    "Sovereign AI Infrastructure: Zero-Egress Air-Gapped LLM Deployments for KSA Enterprise",
    "KV-Cache Prefix Pinning vs Rolling Context Eviction in Long-Horizon Agent Fleets",
    "Zero-Token Deterministic Tabular Envelopes vs Neural Embeddings in Enterprise ETL",
    "Model Context Protocol (MCP) Multi-Tenant Routing & Sub-Millisecond Security Sandboxing",
    "Self-Refining Neural AST Distillation: Autonomous Bug Repair Without Token Burn",
    "Browser-Side Hardware-Aware Inference: Client-Side VRAM Detection & Local Model Sharding"
]

def update_readme_index():
    reports = []
    if REPORTS_DIR.exists():
        for r in sorted(REPORTS_DIR.glob("*.md"), reverse=True):
            title = r.stem
            date_str = ""
            # Extract date if prefixed (YYYY-MM-DD-slug)
            parts = r.name.split("-", 3)
            if len(parts) >= 4 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
                date_str = f"{parts[0]}-{parts[1]}-{parts[2]}"
                slug_name = parts[3].replace(".md", "").replace("-", " ").title()
            else:
                slug_name = r.stem.replace("-", " ").title()

            # Read first header for true title
            with open(r, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("# "):
                        slug_name = line.replace("# ", "").strip()
                        break

            reports.append({
                "date": date_str or "2026",
                "title": slug_name,
                "file": r.name
            })

    table_rows = []
    for rep in reports:
        row = f"| `{rep['date']}` | [{rep['title']}](./reports/{rep['file']}) | [`Read Dossier →`](./reports/{rep['file']}) |"
        table_rows.append(row)

    total_reports = len(reports)
    readme_path = REPO_DIR / "README.md"
    content = f"""# ⚡ Autonomous Deep Research Engine

[![Research Fleet](https://img.shields.io/badge/Research_Fleet-Autonomous%20Gemini%20Flash-blue?style=flat-square&logo=google)](https://github.com/Amz34/deep-research-engine)
[![Reports Published](https://img.shields.io/badge/Whitepapers_Published-{total_reports}-00B8A3?style=flat-square)](https://github.com/Amz34/deep-research-engine)
[![Sovereign Cloud](https://img.shields.io/badge/Enterprise-KSA%20%7C%20GCC%20Aligned-FFC01E?style=flat-square)](https://github.com/Amz34)
[![Daily Dispatch](https://img.shields.io/badge/Daily_Dispatch-10%3A00%20UTC-purple?style=flat-square)](https://github.com/Amz34/deep-research-engine)

Recursive, multi-angle technical research decomposition and executive whitepaper synthesis engine architected by **[Aamir Zameer (@Amz34)](https://github.com/Amz34)** (Principal AI Systems Architect, Az. Consultancy).

---

## 🏛️ Architectural Overview

```mermaid
flowchart TD
    A["Target Technical Topic"] --> B["Recursive Vector Decomposer"]
    B --> C1["Vector 1: Foundational Theory & Math"]
    B --> C2["Vector 2: Systems Throughput & VRAM"]
    B --> C3["Vector 3: Failure Modes & Security"]
    B --> C4["Vector 4: Sovereign Enterprise Blueprint"]
    C1 & C2 & C3 & C4 --> D["Deep Evidence & Trade-off Synthesizer"]
    D --> E["Publication-Grade Whitepaper (.md)"]
    E --> F["Autonomous Git Push & Telegram Alert (@AzGem_Bot)"]
```

---

## 🚀 Key Capabilities

1. **Recursive Multi-Angle Decomposition**:
   - Breaks any engineering topic into non-overlapping architectural vectors (mathematical formulation, SRE constraints, security boundary invariants, and enterprise deployment).
2. **Enterprise Grade Dossiers**:
   - Every report includes **Mermaid architecture diagrams**, **trade-off benchmark matrices**, **asymptotic complexity proofs**, and **sovereign cloud compliance patterns**.
3. **Autonomous Daily Dispatch**:
   - Runs on schedule via cron at **10:00 UTC**, selects the #1 trending topic from the systems ontology, compiles the paper, commits to GitHub, and delivers an executive briefing to Telegram (`@AzGem_Bot`).

---

## 📂 Research Whitepaper Library

| Date | Whitepaper Title | Access Link |
|:---:|:---|:---:|
{chr(10).join(table_rows) if table_rows else "| *Pending* | Autonomous research cycles will populate here. | - |"}

---

## 🛠️ CLI Usage

```bash
# Run deep research on any custom topic:
./deep_research.py run "Speculative Decoding in Multi-Agent Swarms"

# Run autonomous research on today's top trending enterprise theme:
./deep_research.py trending --push

# List all published whitepapers:
./deep_research.py list
```

---

*Architected & Maintained by [Aamir Zameer (@Amz34)](https://github.com/Amz34) · Principal AI Systems Architect at Az. Consultancy.*
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📊 Dashboard updated: {total_reports} research whitepaper(s) indexed.")

def main():
    parser = argparse.ArgumentParser(description="Autonomous Deep Research Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_run = subparsers.add_parser("run", help="Conduct deep research on a specific topic")
    p_run.add_argument("topic", help="Target technical topic to investigate")
    p_run.add_argument("--push", action="store_true", help="Auto git commit and push on completion")

    p_trend = subparsers.add_parser("trending", help="Pick and research today's top trending enterprise theme")
    p_trend.add_argument("--push", action="store_true", default=True, help="Auto git commit and push")

    p_list = subparsers.add_parser("list", help="List all generated research whitepapers")

    p_dash = subparsers.add_parser("dashboard", help="Regenerate README index")

    args = parser.parse_args()
    engine = DeepResearchEngine()

    if args.command == "run":
        report_path = engine.run(args.topic)
        update_readme_index()
        if args.push:
            print("📦 Auto-committing and pushing to GitHub...")
            os.chdir(REPO_DIR)
            subprocess.run(["git", "add", "."], check=False)
            msg = f"feat(research): publish deep research dossier on '{args.topic}'"
            subprocess.run(["git", "commit", "-m", msg], check=False)
            subprocess.run(["git", "push"], check=False)
            print("✅ Pushed to GitHub!")

    elif args.command == "trending":
        # Check existing reports to pick one that hasn't been researched yet
        existing_names = [f.name.lower() for f in REPORTS_DIR.glob("*.md")] if REPORTS_DIR.exists() else []
        candidates = []
        for t in TRENDING_ONTOLOGY:
            slug = t.lower()[:20]
            if not any(slug in e for e in existing_names):
                candidates.append(t)

        chosen = candidates[0] if candidates else random.choice(TRENDING_ONTOLOGY)
        print(f"🔥 Selected Trending Theme: '{chosen}'")
        report_path = engine.run(chosen)
        update_readme_index()

        if args.push:
            print("📦 Auto-committing and pushing to GitHub...")
            os.chdir(REPO_DIR)
            subprocess.run(["git", "add", "."], check=False)
            msg = f"feat(research): publish deep research dossier on '{chosen}'"
            subprocess.run(["git", "commit", "-m", msg], check=False)
            subprocess.run(["git", "push"], check=False)
            print("✅ Pushed to GitHub!")

    elif args.command == "list":
        if not REPORTS_DIR.exists():
            print("No reports found.")
            return
        files = sorted(REPORTS_DIR.glob("*.md"))
        print(f"\n📚 Published Research Whitepapers ({len(files)}):")
        for f in files:
            print(f"  - {f.name}")
        print()

    elif args.command == "dashboard":
        update_readme_index()

if __name__ == "__main__":
    main()
