# Medallion Pipeline

Orchestrates the Lush Protein data lake layers.

## Scripts

| Script | Layer transition | Underlying EDA scripts |
|--------|------------------|------------------------|
| `migrate_to_medallion.py` | Legacy → Medallion layout | One-time file move + junctions |
| `run_bronze_to_silver.py` | Bronze → Silver | `01_load_and_merge` + `run_eda.py` (02–12) |
| `run_silver_to_gold.py` | Silver → Gold | `13_build_finals_datasets` + `enrich_finals_with_margin` |
| `run_gold_analytics.py` | Gold → Analytics | decile, category, `aditya_findings/run_all` |
| `run_full_pipeline.py` | All layers | All of the above |

## Quick start

```bash
# First time: reorganize existing data
python data/pipeline/migrate_to_medallion.py

# Full rebuild from raw
python data/pipeline/run_full_pipeline.py

# Incremental (parquet cache exists)
python data/pipeline/run_full_pipeline.py --skip-load
```

## Configuration

All paths defined in `EDA/00_config.py`:

- `SILVER_DIR` = `data/silver/`
- `GOLD_DIR` = `data/gold/`
- `GOLD_ANALYTICS_*` = `data/gold/analytics/`
