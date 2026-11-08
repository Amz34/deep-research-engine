#!/usr/bin/env python3
"""
Live Autonomous Trending Topic Detector
=======================================
Pulls live trending signals across Hacker News, arXiv CS papers,
and enterprise systems ontologies to autonomously synthesize
high-impact technical research subjects.

Author: Amz34 / Antigravity
"""

import json
import urllib.request
import re
from typing import List, Dict

AI_SYSTEMS_KEYWORDS = [
    "llm", "agent", "gpu", "vram", "inference", "speculative", "kv-cache",
    "distributed", "concurrency", "compiler", "rust", "wasm", "mcp", "rag",
    "vector", "database", "consensus", "raft", "paxos", "security", "sandbox",
    "cloud", "sovereign", "zero-trust", "kernel", "ebpf", "memory"
]

def fetch_hn_top_stories(limit: int = 30) -> List[Dict]:
    """Fetch top engineering stories from Hacker News API."""
    stories = []
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(url, headers={"User-Agent": "AutonomousResearchEngine/1.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            ids = json.loads(resp.read().decode("utf-8"))[:limit]

        for item_id in ids[:15]:
            try:
                item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
                req_item = urllib.request.Request(item_url, headers={"User-Agent": "AutonomousResearchEngine/1.0"})
                with urllib.request.urlopen(req_item, timeout=3) as r:
                    item_data = json.loads(r.read().decode("utf-8"))
                    if item_data and "title" in item_data:
                        stories.append({
                            "title": item_data.get("title", ""),
                            "url": item_data.get("url", ""),
                            "score": item_data.get("score", 0)
                        })
            except Exception:
                continue
    except Exception as e:
        print(f"⚠️ HN fetch notice: {e}")
    return stories

def fetch_arxiv_recent() -> List[str]:
    """Fetch recent submissions from arXiv cs.AI / cs.DC."""
    titles = []
    try:
        url = "https://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.DC&start=0&max_results=8&sortBy=submittedDate&sortOrder=descending"
        req = urllib.request.Request(url, headers={"User-Agent": "AutonomousResearchEngine/1.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            xml_data = resp.read().decode("utf-8")
            raw_titles = re.findall(r'<title>(.*?)</title>', xml_data, re.DOTALL)
            for t in raw_titles[1:]:  # skip feed title
                clean_t = re.sub(r'\s+', ' ', t).strip()
                if clean_t:
                    titles.append(clean_t)
    except Exception as e:
        print(f"⚠️ arXiv fetch notice: {e}")
    return titles

def detect_trending_theme(client, existing_slugs: List[str] = None) -> str:
    """Uses Gemini 2.5 Flash to synthesize current live signals into a flagship topic."""
    if existing_slugs is None:
        existing_slugs = []

    hn_stories = fetch_hn_top_stories()
    arxiv_titles = fetch_arxiv_recent()

    hn_titles = [s["title"] for s in hn_stories]
    combined_signals = "\n".join([f"- HN: {t}" for t in hn_titles[:10]] + [f"- arXiv: {t}" for t in arxiv_titles[:5]])

    prompt = f"""You are the Chief AI Systems Scientist at an enterprise sovereign cloud consultancy.
Given the following real-time signals from Hacker News and recent arXiv papers:

{combined_signals}

Previously researched topics (DO NOT REPEAT or duplicate these):
{json.dumps(existing_slugs)}

Formulate 1 cutting-edge, high-impact enterprise AI/Systems engineering research topic that addresses current industry pain points (e.g. agent orchestration, memory/KV-cache efficiency, sovereign air-gapped security, zero-token deterministic systems, or low-latency high-throughput distributed inference).

Requirements:
- Must read like a publication-grade MIT/Stanford systems paper title or ACM SIGCOMM/OSDI whitepaper.
- Must be specific, rigorous, and relevant to modern production engineering.
- Output ONLY the single title string with no quotes, markdown formatting, or preamble."""

    from google.genai import types
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3
        )
    )
    theme = resp.text.strip().strip('"').strip("'")
    return theme

if __name__ == "__main__":
    from google import genai
    c = genai.Client()
    t = detect_trending_theme(c)
    print("Detected Trending Theme:", t)
