"""
Pipeline orchestrators for the Medallion data lake.

Bronze -> Silver -> Gold -> Analytics

Usage:
    python data/pipeline/run_full_pipeline.py
    python data/pipeline/run_bronze_to_silver.py [--skip-load]
    python data/pipeline/run_silver_to_gold.py
    python data/pipeline/run_gold_analytics.py
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
EDA = BASE / "EDA"
FINDINGS = EDA / "aditya_findings"


def run_script(script: Path, cwd: Path | None = None, label: str = "") -> bool:
    cwd = cwd or script.parent
    print(f"\n{'=' * 65}")
    print(f"  {label or script.name}")
    print(f"{'=' * 65}")
    t0 = time.time()
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(cwd),
        env=env,
    )
    elapsed = time.time() - t0
    ok = result.returncode == 0
    print(f"\n  {'OK' if ok else 'FAILED'} ({elapsed:.1f}s)")
    return ok


def run_eda_module(args_extra: list[str] | None = None) -> bool:
    cmd = [sys.executable, str(EDA / "run_eda.py")] + (args_extra or [])
    print(f"\n{'=' * 65}")
    print("  EDA run_eda.py (Silver layer scripts 01-12)")
    print(f"{'=' * 65}")
    result = subprocess.run(cmd, cwd=str(EDA))
    return result.returncode == 0


def bronze_to_silver(skip_load: bool = False) -> bool:
    print("\n" + "#" * 65)
    print("  BRONZE -> SILVER")
    print("#" * 65)
    extra = ["--skip-load"] if skip_load else []
    return run_eda_module(extra)


def silver_to_gold() -> bool:
    print("\n" + "#" * 65)
    print("  SILVER -> GOLD")
    print("#" * 65)
    steps = [
        (EDA / "13_build_finals_datasets.py", EDA, "13_build_finals_datasets.py"),
        (FINDINGS / "enrich_finals_with_margin.py", FINDINGS, "enrich_finals_with_margin.py"),
    ]
    for script, cwd, label in steps:
        if not script.exists():
            print(f"  [MISSING] {script}")
            return False
        if not run_script(script, cwd, label):
            return False
    return True


def gold_analytics() -> bool:
    print("\n" + "#" * 65)
    print("  GOLD -> ANALYTICS")
    print("#" * 65)
    steps = [
        (EDA / "decile_analysis" / "run_decile_analysis.py", EDA / "decile_analysis", "decile_analysis"),
        (EDA / "decile_analysis" / "run_d1_profile_analysis.py", EDA / "decile_analysis", "d1_profile"),
        (EDA / "run_decile_finals.py", EDA, "run_decile_finals"),
        (EDA / "category_analysis" / "run_category_analysis.py", EDA / "category_analysis", "category_analysis"),
        (EDA / "category_analysis" / "run_decile_category_analysis.py", EDA / "category_analysis", "decile_category"),
        (FINDINGS / "run_all.py", FINDINGS, "aditya_findings/run_all"),
        (FINDINGS / "rec_f_g_validation" / "run_rec_f_g_analysis.py", FINDINGS / "rec_f_g_validation", "rec_f_g_validation"),
    ]
    for script, cwd, label in steps:
        if not script.exists():
            print(f"  [SKIP] {label} — not found")
            continue
        if not run_script(script, cwd, label):
            return False
    return True


def full_pipeline(skip_load: bool = False, skip_analytics: bool = False) -> int:
    failures = []
    if not bronze_to_silver(skip_load):
        failures.append("bronze_to_silver")
    if not silver_to_gold():
        failures.append("silver_to_gold")
    if not skip_analytics and not gold_analytics():
        failures.append("gold_analytics")

    print("\n" + "=" * 65)
    if failures:
        print(f"PIPELINE FAILED: {', '.join(failures)}")
        return 1
    print("MEDALLION PIPELINE COMPLETE")
    print(f"  Silver:    {BASE / 'data' / 'silver'}")
    print(f"  Gold:      {BASE / 'data' / 'gold'}")
    print(f"  Analytics: {BASE / 'data' / 'gold' / 'analytics'}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Medallion pipeline runner")
    parser.add_argument("--skip-load", action="store_true", help="Skip 01_load_and_merge")
    parser.add_argument("--skip-analytics", action="store_true", help="Stop after Gold enrichment")
    args = parser.parse_args()
    sys.exit(full_pipeline(skip_load=args.skip_load, skip_analytics=args.skip_analytics))
