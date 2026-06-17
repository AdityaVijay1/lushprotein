"""
Run all aditya_findings analyses in order.

  python EDA/aditya_findings/run_all.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    ROOT / "enrich_finals_with_margin.py",
    ROOT / "margin_analysis" / "run_margin_analysis.py",
    ROOT / "Recommendation_A" / "run_recommendation_a.py",
    ROOT / "Recommendation_B" / "run_recommendation_b.py",
    ROOT / "recommendation_systems" / "sku_market_basket.py",
    ROOT / "recommendation_systems" / "build_recommenders.py",
    ROOT / "recommendation_systems" / "hierarchical_clustering.py",
    ROOT / "build_pitch_analysis.py",
]

for script in SCRIPTS:
    print(f"\n{'='*60}\nRunning {script.name}\n{'='*60}")
    rc = subprocess.call([sys.executable, str(script)])
    if rc != 0:
        sys.exit(rc)
print("\nAll analyses complete.")
