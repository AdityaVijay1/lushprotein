"""Bronze -> Silver: load raw data and run EDA scripts 01-12."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _runner import bronze_to_silver

if __name__ == "__main__":
    skip = "--skip-load" in sys.argv
    sys.exit(0 if bronze_to_silver(skip_load=skip) else 1)
