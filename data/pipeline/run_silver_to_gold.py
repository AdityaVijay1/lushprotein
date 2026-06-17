"""Silver -> Gold: build finals datasets and enrich with COGS."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _runner import silver_to_gold

if __name__ == "__main__":
    sys.exit(0 if silver_to_gold() else 1)
