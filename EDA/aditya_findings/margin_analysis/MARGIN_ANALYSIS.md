# Margin Analysis — LP COGS Integration

**Script:** `run_margin_analysis.py`  
**COGS source:** `20260616-COGS_Data_Request_LushProtein (1).xlsx`  
**Date:** June 2026

---

## What this does

LP shared unit COGS for **129 SKUs**. We join this to `lines.parquet`, compute **true gross profit** per line and per customer, and compare against the old **40% revenue proxy**.

**Hybrid method (used everywhere downstream):**
- Lines with COGS: `GP = line_revenue - qty × unit_cost`
- Lines without COGS: `GP = line_revenue × 40%` (proxy fallback)
- Customer GP = sum of both

---

## Key numbers (slide-ready)

| Metric | Value |
|--------|-------|
| SKUs with COGS | **129** |
| Line-item coverage | **80.5%** of finals lines |
| Revenue coverage | **74.7%** of finals line revenue |
| Weighted margin (COGS-covered lines) | **70.5%** — not 40% |
| True GP on covered lines | **S$418,263** |
| Old 40% proxy on all revenue | **S$317,786** |

**Implication:** The 40% proxy **understates** margin on hero proteins (Clear/Lean). Profit D1 is even more valuable than we thought.

---

## True profit deciles vs proxy

| Decile | Avg true GP | % of total GP | Avg margin % |
|--------|-------------|---------------|--------------|
| D1 | **S$326** | **41%** | 65.4% |
| D10 | **S$5** | 0.6% | 49.2% |

- **D1 vs D10 gap:** ~**69×** on true GP (was 61× on proxy)
- **Decile rank stability:** 53.7% of customers stay in same decile; D1 membership is directionally stable
- Profit D1 still = **429 customers**, **43% of revenue**, **41% of true GP**

---

## Margin leakage (Recommendation A proof)

If LP runs a **10% site-wide discount** that hits profit D1:

| Scenario | GP at risk |
|----------|------------|
| 10% discount on all profit D1 (429 customers) | **S$14,000/yr** |
| 10% discount on VIP only (245 customers) | **S$8,762/yr** |
| Exclude D1 from blanket promo (Rec A) | **S$0** |

At 15% discount on D1: **S$21K+** GP erosion.

---

## How COGS is used

1. **Sheet "All Sold SKUs"** — 41 SKUs with `unit_cost` from product master
2. **Sheet "MISSING COGS — LP Fill"** — 214 rows with LP-filled `COGS` column
3. Join key: `Line: SKU` on `lines.parquet`
4. Outputs: `sku_true_margin.csv`, `customers_with_true_gp.csv`, `true_profit_decile_summary.csv`

---

## Charts (for deck / report)

| File | Use on slide? |
|------|---------------|
| `fig_proxy_vs_true_gp.png` | Yes — shows COGS changes the story |
| `fig_margin_leakage.png` | Yes — Rec A proof |
| `fig_cogs_coverage.png` | Appendix |
| `fig_top_skus_true_gp.png` | Product depth Q&A |

---

## Regenerate

```bash
python EDA/aditya_findings/margin_analysis/run_margin_analysis.py
```
