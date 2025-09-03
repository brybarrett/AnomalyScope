from __future__ import annotations
import argparse
import difflib
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from dotenv import load_dotenv  # auto-load .env

# Load environment variables from .env at repo root
load_dotenv()

from reporting.generator import AnomalyCard, write_anomaly_outputs
from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider


@dataclass
class ProviderRun:
    name: str
    responses: List[str]
    pairwise: List[Tuple[int, int, float]]
    mean_similarity: float
    min_similarity: float

    @staticmethod
    def seq_sim(a: str, b: str) -> float:
        return difflib.SequenceMatcher(a=a, b=b).ratio()

    @classmethod
    def from_responses(cls, name: str, responses: List[str]) -> "ProviderRun":
        sims: List[Tuple[int, int, float]] = []
        n = len(responses)
        for i in range(n):
            for j in range(i + 1, n):
                sims.append((i, j, cls.seq_sim(responses[i], responses[j])))
        scores = [s for (_, _, s) in sims] or [1.0]
        return cls(
            name=name,
            responses=responses,
            pairwise=sims,
            mean_similarity=float(np.mean(scores)),
            min_similarity=float(np.min(scores)),
        )


def cross_similarity(a: List[str], b: List[str]) -> float:
    """Average best-match similarity across two response sets."""
    if not a or not b:
        return 1.0
    totals = []
    for ai in a:
        best = max(difflib.SequenceMatcher(a=ai, b=bj).ratio() for bj in b)
        totals.append(best)
    for bj in b:
        best = max(difflib.SequenceMatcher(a=bj, b=ai).ratio() for ai in a)
        totals.append(best)
    return float(np.mean(totals)) if totals else 1.0


def classify(sep_cross: float, within: Dict[str, ProviderRun], threshold: float) -> str:
    """
    Severity rules focused on *provider divergence*:
    - If cross-sim < 0.60 -> high
    - elif cross-sim < threshold (default 0.85) -> medium
    - elif any provider within-mean < threshold -> low
    - else none
    """
    if sep_cross < 0.60:
        return "high"
    if sep_cross < threshold:
        return "medium"
    if any(p.mean_similarity < threshold for p in within.values()):
        return "low"
    return "none"


def _update_index_page() -> None:
    """
    Keep GitHub Pages homepage in sync:
    Runs scripts/update_index.py if it exists; logs but never fails the probe.
    """
    script = Path("scripts") / "update_index.py"
    if not script.exists():
        print("[pages] scripts/update_index.py not found; skipping index update.")
        return
    try:
        rc = subprocess.call([sys.executable, str(script)])
        if rc == 0:
            print("[pages] index.md updated from LATEST_ANOMALY.md.")
        else:
            print(f"[pages] update_index.py exited with code {rc} (continuing).")
    except Exception as e:
        print(f"[pages] failed to update index.md: {e!r} (continuing).")


def main():
    ap = argparse.ArgumentParser(description="AnomalyScope cross-provider LIVE probe")
    ap.add_argument("--prompt", default="Explain the purpose of AnomalyScope in one concise sentence.")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--temperature", type=float, default=0.9)
    ap.add_argument("--threshold", type=float, default=0.85)
    ap.add_argument("--providers", default="openai,anthropic", help="comma list (supported: openai,anthropic)")
    args = ap.parse_args()

    # Instantiate providers
    selected = [p.strip().lower() for p in args.providers.split(",") if p.strip()]
    prov_objs = []
    for p in selected:
        if p == "openai":
            prov_objs.append(OpenAIProvider())
        elif p == "anthropic":
            prov_objs.append(AnthropicProvider())
        else:
            raise ValueError(f"Unsupported provider: {p}")

    # Collect runs
    runs: Dict[str, ProviderRun] = {}
    for prov in prov_objs:
        responses = prov.generate(args.prompt, args.temperature, args.runs)
        runs[prov.name] = ProviderRun.from_responses(prov.name, responses)

    # Cross-provider similarity (pairwise on first two selected)
    names = list(runs.keys())
    if len(names) < 2:
        raise RuntimeError("Need at least two providers for cross-provider drift.")
    a, b = names[0], names[1]
    cross_sim = cross_similarity(runs[a].responses, runs[b].responses)

    # Severity classification prioritizes cross divergence
    severity = classify(cross_sim, runs, args.threshold)

    # Prepare card
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    card = AnomalyCard(
        id=f"{a.upper()}-vs-{b.upper()}-DIVERGENCE",
        description=(
            f"Cross-provider drift on prompt with runs={args.runs}, temp={args.temperature}. "
            f"cross_similarity={cross_sim:.3f}; "
            f"{a}: mean={runs[a].mean_similarity:.3f}, min={runs[a].min_similarity:.3f}; "
            f"{b}: mean={runs[b].mean_similarity:.3f}, min={runs[b].min_similarity:.3f}."
        ),
        severity=severity if severity != "none" else "low",
        timestamp=now,
        meta={
            "prompt": args.prompt,
            "threshold": args.threshold,
            "providers": list(runs.keys()),
            "runs": args.runs,
            "temperature": args.temperature,
            "samples": {
                a: runs[a].responses[:3],
                b: runs[b].responses[:3],
            },
            "cross_similarity": cross_sim,
            "within": {
                a: {"mean": runs[a].mean_similarity, "min": runs[a].min_similarity},
                b: {"mean": runs[b].mean_similarity, "min": runs[b].min_similarity},
            },
        },
    )

    paths = write_anomaly_outputs(card)

    # Keep GitHub Pages homepage synced with the latest anomaly
    _update_index_page()

    # Console
    print(f"[🔫] Cross-provider shot: {a} vs {b}")
    print(f"[📈] cross_similarity={cross_sim:.3f}")
    for n in names:
        pr = runs[n]
        print(f"[{n.upper()}] mean={pr.mean_similarity:.3f}  min={pr.min_similarity:.3f}")
    print(f"[🚨] severity={card.severity}")
    print(f"[📝] JSON:    {paths['json']}")
    print(f"[📄] MARKDOWN:{paths['md']}")
    print(f"[📌] Latest:  {paths['latest']}")


if __name__ == "__main__":
    main()
