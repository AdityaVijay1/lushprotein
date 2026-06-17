# Silver Layer

**Path:** `data/silver/` (legacy alias: `EDA/outputs/`)  
**Purpose:** Cleaned, standardized, full-history analytical base.  
**Built from:** Bronze via `01_load_and_merge.py` + scripts `02`–`12`

---

## Silver tables (Parquet)

| File | Grain | Rows (approx) | Description |
|------|-------|---------------|-------------|
| `orders.parquet` | 1 row / order | ~27,350 | All stores, 2020–2026, FX-normalized |
| `lines.parquet` | 1 row / line item | ~51,000 | Product lines only |
| `customers.parquet` | 1 row / customer | ~14,000 | Aggregated from orders |
| `products.parquet` | 1 row / variant | 167 | Product master |
| `discounts.parquet` | 1 row / code | 367 | Discount reference |
| `rc_*.parquet` | varies | filtered | Recharge subscription tables |

---

## Silver exports (CSV)

Prefix indicates producing script:

| Prefix | Script | Contents |
|--------|--------|----------|
| `02_*` | Data quality | Orders by year/country/channel, revenue by month |
| `03_*` | Retention | Cohort heatmap, RFM, time-to-2nd purchase |
| `04_*` | Product | Cross-sell, SKU popularity, repeat by first product |
| `05_*` | Channel/discount | Channel quality, discount sensitivity |
| `06_*` | Subscription | LTV, churn, win-back |
| `07_*`–`11_*` | Five-Lens audit | Deciles, migration, VTD, vintage, health scorecard |
| `12_*` | Finals deep-dive | LTV cohort, loyal repeater, SKU flavor (legacy CSV layer) |

---

## Silver rules

1. **No finals filters** — full customer history, all years
2. **40% margin proxy** used in lens scripts (pre-COGS)
3. **Safe to rebuild** — rerun `run_bronze_to_silver.py` anytime
4. **Do not apply LP-F01–F04 filters here** — that is Gold layer

---

## Regenerate

```bash
python data/pipeline/run_bronze_to_silver.py
```
