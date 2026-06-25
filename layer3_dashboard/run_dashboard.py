#!/usr/bin/env python3
"""One-command launcher for the LushProtein Layer 3 dashboard."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIREMENTS = ROOT / "requirements.txt"
BUILD_SCRIPT = ROOT / "scripts" / "build_demo_data.py"
APP = ROOT / "app.py"

REQUIRED_PACKAGES = [
    "streamlit",
    "pandas",
    "plotly",
    "openpyxl",
    "pyarrow",
]


def ensure_package(pkg: str) -> None:
    if importlib.util.find_spec(pkg) is None:
        print(f"Installing missing package: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])


def ensure_dependencies() -> None:
    print("Checking dependencies...")
    for pkg in REQUIRED_PACKAGES:
        ensure_package(pkg)
    if REQUIREMENTS.exists():
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS), "-q"]
        )
    print("Dependencies OK.")


def ensure_demo_data() -> None:
    data_dir = ROOT / "data"
    needed = [
        data_dir / "customers_demo.csv",
        data_dir / "transactions_demo.csv",
        data_dir / "cross_sell_rules.csv",
    ]
    if all(p.exists() for p in needed):
        print("Demo data found.")
        return
    print("Demo data not found — building anonymised demo dataset...")
    subprocess.check_call([sys.executable, str(BUILD_SCRIPT)])


def launch_streamlit() -> None:
    os.chdir(ROOT)
    print("\nStarting LushProtein Layer 3 Dashboard...")
    print("Open: http://localhost:8501\n")
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(APP),
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false",
        ]
    )


def main() -> None:
    ensure_dependencies()
    ensure_demo_data()
    launch_streamlit()


if __name__ == "__main__":
    main()
