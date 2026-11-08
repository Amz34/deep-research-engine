#!/usr/bin/env /home/ubuntu/.venvs/antigravity/bin/python
"""
Core Autonomous Deep Research Engine
====================================
Recursive multi-angle research decomposition, evidence synthesis,
and executive whitepaper generation.

Author: Amz34 / Antigravity
"""

import os
import sys
import json
import time
import re
from datetime import datetime, timezone
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_DIR / "reports"
TELEGRAM_CFG = Path("/home/ubuntu/.config/telegram/azgem_bot.json")

def send_telegram(html_text: str) -> bool:
    try:
        if not TELEGRAM_CFG.exists():
            return False
        with open(TELEGRAM_CFG, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        token = cfg.get("token")
        chat_id = cfg.get("chat_id")
        if not token or not chat_id:
            return False
        import urllib.request
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = json.dumps({
            "chat_id": chat_id,
            "text": html_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"⚠️ Telegram alert failed: {e}")
        return False

def get_client():
    from google import genai
    import os
    from pathlib import Path
    if not os.environ.get("GEMINI_API_KEY"):
        env_file = Path(__file__).resolve().parent.parent / ".env"
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        os.environ["GEMINI_API_KEY"] = line.strip().split("=", 1)[1].strip('"').strip("'")
                        break
    return genai.Client()

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

class DeepResearchEngine:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.client = get_client()
        self.model_name = model_name

    def _call_gemini_with_retry(self, prompt: str, is_json: bool = False, max_retries: int = 5) -> str:
        from google.genai import types
        from google.genai.errors import ClientError, APIError

        backoff = 5.0
        for attempt in range(max_retries):
            try:
                config = types.GenerateContentConfig(
                    temperature=0.2 if is_json else 0.4,
                    response_mime_type="application/json" if is_json else None
                )
                resp = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                return resp.text.strip()
            except (ClientError, APIError, Exception) as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    wait_time = backoff * (2 ** attempt)
                    print(f"  ⏳ Gemini rate limit encountered (429). Exponential backoff: sleeping {wait_time:.1f}s (attempt {attempt+1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    print(f"  ⚠️ Gemini call attempt {attempt+1} failed ({e}), retrying in {backoff}s...")
                    time.sleep(backoff)
        config = types.GenerateContentConfig(temperature=0.3)
        return self.client.models.generate_content(model=self.model_name, contents=prompt, config=config).text.strip()

    def decompose_topic(self, topic: str) -> list[str]:
        print(f"🔍 [1/3] Decomposing topic into technical vectors: '{topic}'...")
        prompt = f"""You are a Principal AI Systems Architect. Decompose the following technical research topic into 4 distinct, non-overlapping architectural inquiry vectors for a high-level whitepaper:

Research Topic: {topic}

Vectors must cover:
1. Foundational Architecture & Mathematical / Asymptotic Mechanics
2. Systems Engineering & Production SRE Constraints (Throughput, Latency, Memory/VRAM, Network)
3. Failure Modes, Security Boundary Invariants & Edge Cases
4. Enterprise Implementation Blueprint (Sovereign Cloud, Data Residency, High-Availability)

Return ONLY a valid JSON list of 4 strings representing the vector titles. Example:
["Foundational Theory & Algorithmic Mechanics", "Systems Throughput & Resource Trade-offs", "Edge Failure Modes & Security Sandboxing", "Enterprise Sovereign Deployment Blueprint"]"""

        try:
            raw = self._call_gemini_with_retry(prompt, is_json=True)
            vectors = json.loads(raw)
            print(f"  ✅ Generated {len(vectors)} research vectors.")
            return vectors
        except Exception as e:
            print(f"  ⚠️ Fallback to standard vectors: {e}")
            return [
                "Foundational Architecture & Mathematical Formulation",
                "Systems Performance, Latency & VRAM Constraints",
                "Critical Failure Modes & Resilience Patterns",
                "Enterprise Architecture & Deployment Strategy"
            ]

    def investigate_vector(self, topic: str, vector: str) -> str:
        print(f"  🔬 Investigating Vector: '{vector}'...")
        prompt = f"""You are a Principal AI Systems Architect writing an in-depth technical analysis for an executive engineering dossier.

Topic: {topic}
Vector: {vector}

Deliver a rigorous, production-grade technical evaluation of this vector. Include:
- Technical mechanisms, exact data structures, protocols, and mathematical formulas where applicable.
- Concrete architectural trade-offs (e.g. latency vs consistency, token cost vs accuracy, memory overhead vs throughput).
- Concrete code / configuration snippet or architectural invariant.
- Avoid vague introductory fluff; write with senior engineering rigor.

Format in clear GitHub Markdown."""

        res = self._call_gemini_with_retry(prompt, is_json=False)
        time.sleep(2)
        return res

    def synthesize_whitepaper(self, topic: str, vectors: list[str], vector_findings: list[str]) -> str:
        print(f"📑 [3/3] Synthesizing comprehensive Technical Whitepaper...")
        findings_combined = "\n\n".join([f"### {v}\n{f}" for v, f in zip(vectors, vector_findings)])

        prompt = f"""You are a World-Class AI Infrastructure Architect and Principal Fellow at Az. Consultancy.
Synthesize the technical findings below into a comprehensive, publication-grade Research Whitepaper.

Topic: {topic}

Findings Collected Across Inquiry Vectors:
{findings_combined}

Structure the final Whitepaper with these exact sections:
# [Authoritative Whitepaper Title]

**Author:** Aamir Zameer (@Amz34) · Principal AI Systems Architect, Az. Consultancy  
**Date:** {datetime.now(timezone.utc).strftime('%B %d, %Y')}  
**Status:** Approved for Production Architecture  
**Tags:** AI Infrastructure, Systems Engineering, Autonomous Systems  

---

## 1. Executive Abstract
High-density summary of the core engineering thesis, key operational metrics, and quantifiable impact.

## 2. System Architecture & Component Topology
High-level overview of the architectural pattern, accompanied by a clean, error-free GitHub Markdown Mermaid diagram (`mermaid` codeblock) illustrating dataflow, control plane, and boundaries.

## 3. Deep-Dive Architectural Investigation
Synthesize the vector findings into coherent, deeply technical sub-chapters with formulas, code architectures, and algorithmic invariants.

## 4. Benchmark & Trade-off Matrix
A structured Markdown comparison table contrasting this architecture against legacy or alternative paradigms across: Latency, Compute Overhead, Token Burn, Reliability, and Data Residency.

## 5. Enterprise Implementation Blueprint (Saudi Vision 2030 / GCC Sovereign Alignment)
Step-by-step production rollout guide including security jails, network egress controls, and high-availability patterns.

## 6. Citations & Theoretical Grounding
Formal citations referencing key papers (ArXiv, NeurIPS, IEEE, ACM) and foundational open-source ecosystems.

---
Deliver the full, exhaustive Whitepaper in pristine GitHub Flavored Markdown."""

        res = self._call_gemini_with_retry(prompt, is_json=False)
        return res

    def run(self, topic: str) -> Path:
        start_time = time.time()
        print(f"\n🚀 [DEEP RESEARCH ENGINE] Initiating Autonomous Investigation on: '{topic}'")
        print("=" * 70)

        # 1. Decompose
        vectors = self.decompose_topic(topic)

        # 2. Investigate each vector
        findings = []
        for v in vectors:
            f = self.investigate_vector(topic, v)
            findings.append(f)

        # 3. Synthesize
        whitepaper = self.synthesize_whitepaper(topic, vectors, findings)

        # 4. Save
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        slug = slugify(topic)
        filename = f"{date_str}-{slug}.md"
        report_path = REPORTS_DIR / filename
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(whitepaper)

        elapsed = time.time() - start_time
        print(f"\n✅ Whitepaper completed in {elapsed:.1f}s!")
        print(f"📄 Saved to: {report_path}")

        # 5. Telegram Alert
        first_p = ""
        for line in whitepaper.split("\n"):
            if line.strip() and not line.startswith("#") and not line.startswith("**"):
                first_p = line[:240] + "..."
                break

        tele_alert = f"""🔬 <b>Autonomous Deep Research Published</b>
<b>Topic:</b> {topic}
<b>Author:</b> @Amz34 (Az. Consultancy)
<b>Dossier:</b> <code>reports/{filename}</code>
<b>Time:</b> {elapsed:.1f}s

📝 <b>Executive Abstract:</b>
<i>{first_p}</i>

🌐 <a href="https://github.com/Amz34/deep-research-engine/blob/main/reports/{filename}">Read Full Whitepaper on GitHub</a>"""
        send_telegram(tele_alert)

        return report_path
