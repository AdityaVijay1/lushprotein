"""Gold -> Analytics: decile, category, findings, recommendations."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _runner import gold_analytics

if __name__ == "__main__":
    sys.exit(0 if gold_analytics() else 1)
