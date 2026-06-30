"""One-off exploration for new_potential_analysis.md"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
orders = pd.read_parquet(ROOT / "outputs_finals/orders.parquet")
lines = pd.read_parquet(ROOT / "outputs_finals/lines.parquet")
dec = pd.read_csv(ROOT / "outputs_finals/decile_customer_table.csv")
crm = pd.read_csv(ROOT / "outputs_finals/crm_treatment_tiers.csv")

print("=== DISCOUNT CODES ===")
if "discount_codes" in orders.columns:
    codes = orders["discount_codes"].dropna().astype(str)
    print(codes.value_counts().head(20))
elif "discount_code" in orders.columns:
    codes = orders["discount_code"].dropna()
    print(codes.value_counts().head(20))
else:
    print("cols:", [c for c in orders.columns if "disc" in c.lower()])

orders["order_date"] = pd.to_datetime(orders["order_date"])
orders["ym"] = orders["order_date"].dt.to_period("M").astype(str)
print("\n=== MONTHLY ORDERS (top) ===")
print(orders.groupby("ym").size().sort_values(ascending=False).head(10))

price_col = "Price: Total" if "Price: Total" in orders.columns else "total_price"
p = orders[price_col].astype(float)
print(f"\n=== BASKET ({price_col}) ===")
print("median", p.median(), "mean", p.mean())
for th in [60, 80, 100, 120]:
    print(f">=S{th}: {(p>=th).mean()*100:.1f}%")

lines["title_l"] = lines["Line: Title"].str.lower() if "Line: Title" in lines.columns else lines.get("title", pd.Series(dtype=str)).str.lower()
creatine = set(lines[lines["title_l"].str.contains("creatine", na=False)]["order_id"])
protein = set(lines[lines["title_l"].str.contains("protein|collagen", na=False)]["order_id"])
print("\n=== CREATINE ===")
print("creatine orders", len(creatine), "creatine+protein", len(creatine & protein))

sachet_mask = lines["title_l"].str.contains("sachet|single serve|40g|25g", na=False, regex=True)
s_orders = lines.loc[sachet_mask, "order_id"].unique()
o2c = orders.set_index("order_id")["customer_id"].astype(str).to_dict()
s_cust = {o2c[o] for o in s_orders if o in o2c}
crm["customer_id"] = crm["customer_id"].astype(str)
tier_tot = crm.groupby("crm_treatment_tier").size()
tier_sach = crm[crm["customer_id"].isin(s_cust)].groupby("crm_treatment_tier").size()
print("\n=== SACHET BUYER RATE BY TIER ===")
print((tier_sach / tier_tot * 100).round(1))

pm = "profit_margin_decile" if "profit_margin_decile" in dec.columns else "contribution_margin_decile"
print("\n=== SUB RATE BY PM DECILE ===")
print(dec.groupby(pm)["ever_subscribed"].mean().round(3))

print("\n=== PEACH/OOLONG LINES ===")
title_col = "Line: Title" if "Line: Title" in lines.columns else "title"
po = lines[lines["title_l"].str.contains("oolong|peach", na=False)]
print(po[title_col].value_counts().head(8))

print("\n=== DISCOUNT ORDERS ===")
if "has_discount" in orders.columns:
    print("has_discount rate:", orders["has_discount"].mean())
    disc = orders[orders["has_discount"] == True]
    print("disc orders:", len(disc), "avg basket:", disc[price_col].mean())
    print("no disc avg basket:", orders[orders["has_discount"] != True][price_col].mean())

print("\n=== TAGS (HYROX sample) ===")
if "Tags" in orders.columns:
    hyrox = orders[orders["Tags"].astype(str).str.contains("hyrox|HYROX|gym|GYM|event", case=False, na=False)]
    print("event-tagged orders:", len(hyrox))
    print(hyrox["ym"].value_counts().head(8))
