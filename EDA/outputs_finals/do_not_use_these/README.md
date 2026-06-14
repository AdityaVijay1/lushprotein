# do_not_use_these — reference snapshots only

These `*_dq_clean.parquet` files are **DQ-only** reference outputs from `13_build_finals_datasets.py`.
They still contain all order dates and have **not** had LP-F03 customer exclusion applied.

For all analysis (deciles, deep dives, finals report), use the primary files in the parent folder:
- `orders.parquet`
- `customers.parquet`
- `lines.parquet`
