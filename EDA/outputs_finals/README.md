# Legacy path — Medallion migration

**This folder has moved to the Gold layer.**

| Old path | New canonical path |
|----------|-------------------|
| `EDA/outputs_finals/` | **`data/gold/`** |
| `EDA/outputs/` | **`data/silver/`** |

All pipeline scripts now use paths from `EDA/00_config.py`:
- `SILVER_DIR` = `data/silver/`
- `FINALS_DIR` / `GOLD_DIR` = `data/gold/`

See **`data/README.md`** for the full Medallion architecture.

## Regenerate Gold layer

```bash
python data/pipeline/run_silver_to_gold.py
```

## Gold reference (DQ snapshots)

`data/gold/reference/` — was `do_not_use_these/`
