import pandas as pd
import sys
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
REC = Path("EDA/aditya_findings/recommendation_systems/outputs")

# L3 core: cross-sell timing and samples
timing = pd.read_csv(REC / "cross_sell_timing_and_samples.csv")
print("=== CROSS SELL TIMING AND SAMPLES ===")
print("Cols:", timing.columns.tolist())
print(timing.to_string())
print()

# Next best SKU per first purchase
nbs = pd.read_csv(REC / "next_best_sku_per_first.csv")
print("=== NEXT BEST SKU PER FIRST PURCHASE ===")
print("Cols:", nbs.columns.tolist())
print(nbs.head(20).to_string())
print()

# First to second SKU matrix
f2s = pd.read_csv(REC / "first_to_second_sku_matrix.csv")
print("=== FIRST TO SECOND SKU MATRIX ===")
print("Cols:", f2s.columns.tolist())
print(f2s.head(15).to_string())
print()

# Rule-based recommendations (L1)
rules = pd.read_csv(REC / "recommender_01_rule_based.csv")
print("=== L1 RULE BASED ===")
print(rules.head(15).to_string())
print()

# Association rules (L2)
assoc = pd.read_csv(REC / "sku_association_rules.csv")
print("=== SKU ASSOCIATION RULES (L2) ===")
print(assoc.head(15).to_string())
