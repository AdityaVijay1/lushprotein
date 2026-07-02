"""Execute code cells from generated notebooks to verify they run."""
import json
import sys
import matplotlib
matplotlib.use("Agg")
import traceback
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent


def run_notebook(path: Path) -> None:
    print(f"\n{'='*60}\nRunning {path.name}\n{'='*60}")
    nb = json.loads(path.read_text(encoding="utf-8"))
    ns = {"__name__": "__main__", "display": print}
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell["source"])
        if not src.strip():
            continue
        print(f"  cell {i}...", end=" ", flush=True)
        try:
            exec(compile(src, f"{path.name}:cell{i}", "exec"), ns)
            print("OK")
        except Exception as e:
            print("FAIL")
            traceback.print_exc()
            raise SystemExit(1) from e
    print(f"SUCCESS: {path.name}")


if __name__ == "__main__":
    for name in ("solution_1_from_raw.ipynb", "EDA_from_raw.ipynb"):
        run_notebook(ROOT / name)
