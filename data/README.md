# Lush Protein — Medallion Data Lake

**Architecture:** [Databricks Medallion](https://www.databricks.com/glossary/medallion-architecture)  
**Pattern:** Bronze (raw) → Silver (cleaned) → Gold (business-ready) → Analytics (derived)

---

## Layer overview

| Layer | Path | What lives here | Mutability |
|-------|------|-----------------|------------|
| **Bronze** | `data/bronze/` | Raw source catalog + supplemental reference files | Append-only; never transform in place |
| **Silver** | `data/silver/` | Cleaned, FX-converted, merged Parquet + lens CSV exports | Rebuilt from Bronze |
| **Gold** | `data/gold/` | Finals-filtered cohort tables + COGS enrichment | Rebuilt from Silver |
| **Gold / reference** | `data/gold/reference/` | DQ-only audit snapshots (not for analysis) | Rebuilt from Silver |
| **Gold / analytics** | `data/gold/analytics/` | Decile, category, findings, recommendations | Rebuilt from Gold |

**Scripts** stay in `EDA/` — only **data** is reorganized into the lake.

---

## Pipeline (run in order)

```bash
# Full pipeline
python data/pipeline/run_full_pipeline.py

# Or layer by layer:
python data/pipeline/run_bronze_to_silver.py    # 01_load_and_merge + EDA 02–12
python data/pipeline/run_silver_to_gold.py      # 13_build_finals + COGS enrich
python data/pipeline/run_gold_analytics.py      # decile + category + aditya_findings
```

**One-time migration** (if upgrading from pre-medallion layout):

```bash
python data/pipeline/migrate_to_medallion.py
```

---

## Backward compatibility

Legacy paths are preserved as **directory junctions** so existing scripts and docs still resolve:

| Legacy path | Points to |
|-------------|-----------|
| `EDA/outputs/` | `data/silver/` |
| `EDA/outputs_finals/` | `data/gold/` |
| `EDA/decile_analysis/outputs/` | `data/gold/analytics/decile/` |
| `EDA/category_analysis/outputs/` | `data/gold/analytics/category/` |
| `EDA/aditya_findings/*/outputs/` | `data/gold/analytics/findings/<module>/` |

All paths are also defined in `EDA/00_config.py` as `SILVER_DIR`, `GOLD_DIR`, etc.

---

## Data flow

```
Bronze (raw xlsx/csv in 1.* – 5.* folders)
    │
    ▼  01_load_and_merge.py
Silver (data/silver/*.parquet + 02–12 CSV exports)
    │
    ▼  13_build_finals_datasets.py
Gold core (data/gold/orders|lines|customers.parquet)
    │
    ▼  enrich_finals_with_margin.py
Gold enriched (+ true_gross_profit, profit_decile_true, crm_tier)
    │
    ▼  decile_analysis / category_analysis / aditya_findings
Gold analytics (data/gold/analytics/)
    │
    ▼  visualizations/
Presentation charts
```

---

## Which layer to use

| Task | Layer | Path |
|------|-------|------|
| Reload raw Shopify exports | Bronze | `1.customer_transaction/` |
| Full-history midterm analysis | Silver | `data/silver/` |
| Finals cohort (2022+ LP filters) | Gold | `data/gold/*.parquet` |
| True GP / CRM tiers | Gold enriched | `data/gold/customers.parquet` |
| Customer deciles (4,290 pool) | Gold analytics | `data/gold/analytics/decile/` |
| Category ladder / recommendations | Gold analytics | `data/gold/analytics/findings/` |

See layer READMEs: `bronze/README.md`, `silver/README.md`, `gold/README.md`.
