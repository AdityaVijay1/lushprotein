# SKU Market Basket Analysis (Phase 2)

**Script:** `sku_market_basket.py`  
**Input:** `EDA/outputs_finals/lines.parquet` (8,955 orders)

---

## Outputs

| File | Rows | Use |
|------|------|-----|
| `sku_association_rules.csv` | Top 20 | PDP bundles, "frequently bought together" |
| `sku_association_rules_full.csv` | 46 | Full rule set |
| `first_to_second_sku_matrix.csv` | 739 | Post-purchase next-best SKU |
| `next_best_sku_per_first.csv` | ~100 | One recommendation per first-purchase SKU |

---

## Top same-order rules (confidence)

| If customer buys… | Also buys… | Confidence | Lift |
|-------------------|------------|------------|------|
| Lean TMT (1kg) | Clear shaker (White) | **93%** | 10.2× |
| Lean Taro (1kg) | Lean TMT | **92%** | 53× |
| Clear sachet White Grape | Clear sachet Peach | **71%** | 27.7× |
| Clear Peach 500g | Clear White Grape 500g | **36%** | 2.5× |
| Lean Taro 1kg | Lean TMT 1kg | **36%** | 2.9× |

**Product insight:** Flavour exploration within Clear (Peach ↔ White Grape) and Lean (Taro ↔ TMT) is the strongest same-basket signal. Shaker attach is high when protein is in cart.

---

## Top sequential rules (1st order → 2nd order)

For repeaters, the most common 2nd purchase after Clear Peach is **Clear White Grape** (same category, different flavour) — then Lean TMT.

**Actionable:** Post-purchase email at order 2 should recommend **complementary flavour or category**, not a generic homepage link.

---

## Method

- **Support threshold:** 0.5% of orders
- **Confidence threshold:** 5%
- **Sequential:** Customers with 2+ orders; map 1st-order SKUs to 2nd-order SKUs

---

## Regenerate

```bash
python EDA/aditya_findings/recommendation_systems/sku_market_basket.py
```
