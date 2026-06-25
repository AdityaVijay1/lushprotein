# LushProtein Layer 3 Customer Recommendation Dashboard

A founder-demo-ready Streamlit dashboard that shows how **Layer 3 post-purchase recommendations** work: lookup a customer by ID, see what to recommend, which sample to ship, and when to contact them before their expected reorder window.

> **Demo only.** Customer names and areas are anonymised. No email, phone, or full addresses are shown.

---

## Quick Start (One Command)

```bash
cd layer3_dashboard
python run_dashboard.py
```

This will:
1. Check and install Python dependencies
2. Build demo datasets if missing (`data/customers_demo.csv`, `data/transactions_demo.csv`)
3. Launch the Streamlit app at **http://localhost:8501**

---

## What It Demonstrates

| Input | Output |
|---|---|
| Customer ID | Name, last purchase, transaction date |
| First product category | Recommended cross-sell product |
| Reorder interval rules | Sample SKU to ship |
| Timing logic | Days until sample / expected reorder |
| Timeline | Purchase → Email → Sample → Reorder |

### Eligibility Rules (Layer 3 demo scope)

- **Exactly 1 order** (first-time buyer)
- **Purchased in the last 30 days** (relative to demo reference date: 26 Jun 2026)

---

## Project Structure

```
layer3_dashboard/
├── app.py                    # Streamlit dashboard UI
├── run_dashboard.py          # One-command launcher
├── l3_engine.py              # Data loading + Layer 3 recommendation logic
├── requirements.txt
├── README.md
├── .streamlit/config.toml    # Theme
├── data/
│   ├── customers_demo.csv    # Anonymised customer profiles
│   ├── transactions_demo.csv # Recent first-order transactions
│   └── cross_sell_rules.csv  # Layer 3 timing + routing rules
└── scripts/
    ├── build_demo_data.py    # Rebuild demo CSVs from project order data
    └── analyze_data.py       # Data exploration helper
```

---

## Architecture

```
Customer ID lookup
       │
       ▼
Normalize ID (plain numeric / scientific notation)
       │
       ▼
Join customers_demo + transactions_demo
       │
       ▼
Filter: 1 order + last 30 days
       │
       ▼
Map first product category → cross_sell_rules.csv
       │
       ▼
Return CRM actions:
  • Recommended product
  • Sample SKU
  • Email day / sample day / reorder day
  • Timeline visualization
```

### Recommendation Logic (Layer 3)

Rules come from `cross_sell_rules.csv` (derived from LushProtein D1 co-purchase analysis):

| First Purchase | Recommend | Sample | Email Day | Sample Day | Reorder Day |
|---|---|---|---|---|---|
| Clear Protein | Lean Protein | Lean 40g single-serve | 14 | 44 | 54 |
| Lean Protein | Clear Protein | Clear 25g sachet | 14 | 25 | 35 |
| Collagen Glow | Clear Protein | Clear 25g sachet | 21 | 32 | 42 |
| Accessories | Lean Protein | Clear 25g sachet | 7 | 25 | 35 |
| Soy Protein | Clear Protein | Clear/Lean sachet | 14 | 74 | 84 |

**Sample timing:** `median_reorder_days - 10 day buffer` (ship sample before reorder decision).

---

## Rebuild Demo Data

If you have access to the full LushProtein project data locally:

```bash
cd layer3_dashboard
python scripts/build_demo_data.py
```

This reads:
- `../1.customer_transaction/customers_export_20260622.xlsx`
- `../EDA/outputs_finals/orders.parquet`

And writes anonymised demo CSVs into `data/`. Real names are replaced with demo names (e.g. Aditya Vijay, Shwe Tin Aung). Customer IDs remain valid for join testing but no PII is exposed in the UI.

---

## Deployment (Free)

### Option 1: Streamlit Community Cloud (Recommended)

1. Push `layer3_dashboard/` to a GitHub repository
2. Ensure `data/customers_demo.csv` and `data/transactions_demo.csv` are committed (anonymised — safe to deploy)
3. Go to [share.streamlit.io](https://share.streamlit.io)
4. **New app** → connect repo
5. Set **Main file path:** `layer3_dashboard/app.py`
6. Deploy

**Note:** Do not commit raw `customers_export_20260622.xlsx` — only the anonymised CSVs.

### Option 2: Render (Free Tier)

1. Create a new **Web Service** on [render.com](https://render.com)
2. Build command: `pip install -r layer3_dashboard/requirements.txt`
3. Start command: `streamlit run layer3_dashboard/app.py --server.port=$PORT --server.address=0.0.0.0`

### Option 3: Railway

1. Connect GitHub repo at [railway.app](https://railway.app)
2. Set start command: `streamlit run layer3_dashboard/app.py --server.port=$PORT --server.address=0.0.0.0`
3. Railway free tier may have usage limits — check current plan

---

## Security & Privacy

- Only **Customer ID, name (demo), area, and purchase info** shown after lookup
- No email, phone, or street address displayed
- Demo disclaimer shown on every page
- Raw PII Excel files are **not** bundled with the dashboard

---

## Example Lookup

1. Open the dashboard
2. Pick a Customer ID from the sidebar (120 eligible demo customers)
3. Click **Look up customer**

Example output:

| Field | Value |
|---|---|
| Name | Aditya Vijay |
| Last Bought Product | CLEAR PROTEIN |
| Recommended Product | Lean Protein |
| Sample To Ship | Lean 40g single-serve |
| Time To Send Sample | 44 days |
| Estimated Reorder | 54 days |

---

## Requirements

- Python 3.10+
- See `requirements.txt`

Manual install:

```bash
pip install -r requirements.txt
streamlit run app.py
```
