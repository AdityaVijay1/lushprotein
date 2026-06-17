"""Full Medallion pipeline: Bronze -> Silver -> Gold -> Analytics."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _runner import full_pipeline

if __name__ == "__main__":
    skip_load = "--skip-load" in sys.argv
    skip_analytics = "--skip-analytics" in sys.argv
    sys.exit(full_pipeline(skip_load=skip_load, skip_analytics=skip_analytics))
