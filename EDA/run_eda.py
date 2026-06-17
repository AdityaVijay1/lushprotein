"""
run_eda.py  -  Orchestrator: runs all EDA scripts in order.

Usage
-----
    cd <project_root>/EDA
    python run_eda.py

    # Or run a single module:
    python run_eda.py --only 03

Flags
-----
--skip-load   Skip 01_load_and_merge (use if Parquet cache already exists)
--only N      Run only script number N (01-06)
"""

import subprocess
import sys
import os
import time
from pathlib import Path

EDA_DIR = Path(__file__).parent

SCRIPTS = [
    ("01", "01_load_and_merge.py",          "Load raw Excel files -> Parquet cache"),
    ("02", "02_data_quality.py",            "Data quality audit & descriptive stats"),
    ("03", "03_customer_retention.py",      "Retention cohorts, time-to-2nd-purchase, RFM"),
    ("04", "04_product_analysis.py",        "Product stickiness, SKU popularity, cross-sell"),
    ("05", "05_channel_discount.py",        "Channel quality & discount sensitivity"),
    ("06", "06_subscription_churn.py",      "Subscription LTV, churn reasons, win-backs"),
    # -- 5-Lens Customer-Base Audit (Bruce, Fader & Ross 2022) --------------
    ("07", "07_lens1_heterogeneity.py",     "Lens 1: Distributions, deciles, decomposition"),
    ("08", "08_lens2_period_decomposition.py","Lens 2: New/Retained/Lost, migration matrix, up-down"),
    ("09", "09_lens3_cohort_evolution.py",  "Lens 3: Cohort tracking, VTD, inter-purchase time"),
    ("10", "10_lens4_vintage_comparison.py","Lens 4: Vintage quality comparison, channel/discount drift"),
    ("11", "11_lens5_base_health.py",       "Lens 5: Full base health, waterfall, integrated scorecard"),
    ("12", "12_finals_deep_dive.py",         "Finals: LTV cohort/channel, POS vs web, loyal profile, business value"),
]

def run_script(script_file: Path, label: str) -> bool:
    print(f"\n{'='*65}")
    print(f"  {label}")
    print(f"  Running: {script_file.name}")
    print(f"{'='*65}")
    t0 = time.time()
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, str(script_file)],
        capture_output=False,
        cwd=str(EDA_DIR),
        env=env,
    )
    elapsed = time.time() - t0
    if result.returncode == 0:
        print(f"\n  OK  ({elapsed:.1f}s)")
        return True
    else:
        print(f"\n  FAILED (exit code {result.returncode}, {elapsed:.1f}s)")
        return False

def main():
    args = sys.argv[1:]
    skip_load = "--skip-load" in args
    only_num  = None
    if "--only" in args:
        idx = args.index("--only")
        only_num = args[idx + 1]

    print("\nLushProtein EDA Pipeline")
    print("=" * 65)

    failures = []
    for num, fname, label in SCRIPTS:
        if only_num and num != only_num:
            continue
        if skip_load and num == "01":
            print(f"  [SKIPPED] {fname}")
            continue

        script_path = EDA_DIR / fname
        if not script_path.exists():
            print(f"  [MISSING] {fname}")
            continue

        ok = run_script(script_path, label)
        if not ok:
            failures.append(fname)

    print("\n" + "=" * 65)
    if failures:
        print(f"COMPLETED WITH ERRORS: {', '.join(failures)}")
        sys.exit(1)
    else:
        print("ALL SCRIPTS COMPLETED SUCCESSFULLY")
        # Import config for medallion path
        import importlib.util
        _spec = importlib.util.spec_from_file_location("lp_config", EDA_DIR / "00_config.py")
        _cfg = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_cfg)
        print(f"\nSilver layer saved to: {_cfg.SILVER_DIR}")

if __name__ == "__main__":
    main()
