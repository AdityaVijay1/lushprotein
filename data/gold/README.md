# Gold Layer

**Path:** `data/gold/` (legacy alias: `EDA/outputs_finals/`)  
**Purpose:** Business-ready finals cohort + enriched margin + derived analytics.  
**Built from:** Silver via `13_build_finals_datasets.py` → `enrich_finals_with_margin.py`

---

## Gold core tables (Parquet)

Primary analytical tables — **single source of truth** for all finals work.

| File | Rows (approx) | Key columns (post-enrichment) |
|------|---------------|-------------------------------|
| `orders.parquet` | 8,955 | `order_gp`, `order_margin_pct`, `n_categories` |
| `lines.parquet` | 14,448 | `unit_cost`, `gross_profit`, `margin_pct`, `pack_size` |
| `customers.parquet` | 5,694 | `true_gross_profit`, `profit_decile_true`, `crm_tier`, `n_categories_ever` |
| `lines_sku_analysis.parquet` | 14,448 | Lines + `flavor_sku` |
| `products.parquet` | 167 | `unit_cost_lp`, `has_lp_cogs` |
| `discounts.parquet` | 367 | Reference |
| `rc_*.parquet` | scoped | Recharge filtered to finals cohort |

**Manifest:** `manifest.json` · **COGS summary:** `margin_enrichment_summary.json`

---

## Filter stack (Silver → Gold)

Applied in `13_build_finals_datasets.py`:

### LP-F03 — customer cut

**Rule:** If a customer's lifetime `first_order_date` is before 2022-01-01, drop the **entire customer**.

| Layer | Rule |
|-------|------|
| DQ | DQ-02/03/04 — zero revenue, free fulfilments, wholesale |
| LP-F03 | Lifetime `first_order_date >= 2022-01-01` |
| LP-F01 | Exclude `better-whey-protein-elite` buyers |
| LP-F02 | Exclude Jul/Nov acquisition months |
| LP-F04 | Exclude 51%+ discounted first retained order |
| LP-F0 | `order_date >= 2022-01-01` on retained customers |
| Seasonal | Drop Jul/Nov order months; exclude elite handle from lines |

---

## Gold / reference (`data/gold/reference/`)

DQ-cleaned snapshots **without** LP-F03 customer cut.  
**Do not use for analysis** — audit trail only.  
Legacy name: `do_not_use_these/`

---

## Gold / analytics (`data/gold/analytics/`)

| Subfolder | Source scripts | Contents |
|-----------|----------------|----------|
| `decile/` | `run_decile_analysis.py`, `run_d1_profile_analysis.py` | Decile tables, migration, D1 profile |
| `category/` | `run_category_analysis.py`, `run_decile_category_analysis.py` | T1–T9 category × decile CSVs |
| `findings/` | `aditya_findings/run_all.py` | Margin, recommendations, pitch, MBA |

Legacy aliases: `EDA/decile_analysis/outputs/`, `EDA/category_analysis/outputs/`, `EDA/aditya_findings/*/outputs/`

---

## Gold enrichment (COGS)

`enrich_finals_with_margin.py` adds true gross profit using LP COGS (74.7% revenue coverage, 70.5% weighted margin).

**Hybrid GP:** COGS lines use `revenue − qty×cost`; uncovered lines use 40% proxy.

---

## Regenerate

```bash
python data/pipeline/run_silver_to_gold.py      # core tables
python data/pipeline/run_gold_analytics.py      # derived analytics
```
