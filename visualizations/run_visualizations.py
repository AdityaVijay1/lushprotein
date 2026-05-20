"""
run_visualizations.py  -  Generate all presentation charts.

Usage
-----
    cd <project_root>/visualizations
    python run_visualizations.py

All charts saved to: visualizations/charts/*.png
"""
import subprocess, sys, time
from pathlib import Path

VIZ_DIR = Path(__file__).parent
SCRIPTS = [
    ("01_revenue_and_volume.py",   "Revenue trend, discount escalation, monthly chart"),
    ("02_retention_overview.py",   "Retention by channel/product, time-to-2nd, cohort heatmap"),
    ("03_product_and_crosssell.py","Cross-sell LTV, product mix, SKU loyalty, combos"),
    ("04_subscription_churn.py",   "Sub vs one-time, churn by cycle, cancellation reasons"),
    ("05_discount_channel.py",     "Discount depth, marketplace vs web, RFM, code taxonomy"),
]

print("LushProtein Visualization Pipeline")
print("=" * 60)
total_start = time.time()
errors = []

for fname, label in SCRIPTS:
    path = VIZ_DIR / fname
    print(f"\n[{fname}]  {label}")
    t0 = time.time()
    env = {"PYTHONIOENCODING": "utf-8", **__import__("os").environ}
    result = subprocess.run([sys.executable, str(path)], cwd=str(VIZ_DIR), env=env)
    elapsed = time.time() - t0
    if result.returncode != 0:
        print(f"  FAILED ({elapsed:.1f}s)")
        errors.append(fname)
    else:
        print(f"  OK ({elapsed:.1f}s)")

print("\n" + "=" * 60)
elapsed_total = time.time() - total_start
if errors:
    print(f"COMPLETED WITH ERRORS: {', '.join(errors)}")
    sys.exit(1)
else:
    charts = list((VIZ_DIR / "charts").glob("*.png"))
    print(f"ALL DONE in {elapsed_total:.1f}s  |  {len(charts)} charts saved to: {VIZ_DIR / 'charts'}")
    for c in sorted(charts):
        print(f"  {c.name}")
