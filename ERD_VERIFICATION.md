# Group1_ERD.drawio — Verification Report

**Date:** 2026-05-28  
**Verified against:** `deliverables/LushProtein_Orders_STTM.csv`, `README.md` §7–8, pipeline (`01_load_and_merge.py`, `DATA_QUALITY_REPORT_FINAL.md`)  
**Diagram file:** `Group1_ERD.drawio`  
**Audit script:** `python deliverables/parse_erd.py`

All requested ORDERS fixes are in place, the diagram was audited against the STTM and datasets, and gaps were closed. This document is the marker-ready record of what changed and why.

---

## Session outcome (quick reference)

| Area | Status |
|------|--------|
| Your four ORDERS PK/FK fixes | **Correct** — applied and verified |
| ORDERS ↔ PRODUCT MASTER joins | **Correct** — both `line_product_handle` and `line_SKU` now have edges |
| Missing CUSTOMERS entity | **Fixed** — `CUSTOMERS (derived)` added with FK edge from `customer_ID` |
| Missing checkout target | **Fixed** — `SHOPIFY_CHECKOUT (logical)` added; dashed edge (optional FK, ~65–70% null) |
| Recharge cluster | **Mostly correct** — relationships match README; Recharge `customer_id` ≠ Shopify `customer_id` (see caveats) |
| SESSIONS BY REFERRER | **Clarified** — dashed conceptual edge + on-diagram label (no real FK) |
| Denormalized ORDERS table | **Acceptable** — matches raw Shopify export grain; note for slides below |

---

## Your four ORDERS changes — all correct

| Change | Verdict |
|--------|---------|
| Remove `line_variant_ID` as PK/FK | **Correct** — attribute only (~24k duplicates) |
| Add `line_product_handle` as FK | **Correct** — primary join to `products.Handle` |
| Remove `line_product_ID` as FK | **Correct** — ~68% null, not used in joins |
| Add `checkout_ID` as FK | **Correct** — order-level Shopify checkout (~30–35% populated) |

---

## Additional fixes applied

| Fix | Detail |
|-----|--------|
| **CUSTOMERS (derived)** | New entity + **solid** edge from `ORDERS.customer_ID` |
| **SHOPIFY_CHECKOUT (logical)** | New entity + **dashed** edge from `ORDERS.checkout_ID` (no separate CSV; ~65–70% null) |
| **Product join by handle** | `ORDERS.line_product_handle` → `PRODUCT MASTER.handle` — new edge alongside existing `line_SKU` → `variant_SKU` |
| **SESSIONS BY REFERRER** | Edge made **dashed** with on-diagram note: no real FK (campaigns file has no order/customer ID) |

---

## Overall verdict

The ERD is **correct for the deliverable** after these updates. Relationships match the data and `deliverables/LushProtein_Orders_STTM.csv`.

Remaining items below are **documentation caveats for slides**, not diagram errors.

---

## Caveats to mention in slides (not diagram errors)

1. **Denormalized ORDERS** — One wide table (raw Shopify export). README also describes split `orders` / `lines` in the pipeline — both are valid if you note grain (e.g. *“Pipeline normalizes to `orders.parquet` + `lines.parquet`; this ERD shows the source export shape.”*).
2. **DISCOUNTS → ORDERS** — Soft link via `Tags`, not a hard FK.
3. **Recharge `customer_id`** — Recharge namespace, not Shopify `customer_id` (DQ-11).
4. **Dual PK on ORDERS** (`ID` + `line_ID`) — Intentional for line-level grain in the export.

---

## Files updated (this session)

| File | Role |
|------|------|
| `Group1_ERD.drawio` | All structural fixes (PK/FK, new entities, edges, SESSIONS styling) |
| `ERD_VERIFICATION.md` | Full entity-by-entity audit (this document) |
| `deliverables/fix_erd_entities.py` | Script that added CUSTOMERS, SHOPIFY_CHECKOUT, and missing edges |
| `deliverables/parse_erd.py` | Re-run anytime: `python deliverables/parse_erd.py` |

---

## Layout note (draw.io)

Open `Group1_ERD.drawio` in draw.io and confirm:

1. `line_product_handle` and `checkout_ID` show **FK** in the key column.
2. `line_product_ID` and `line_variant_ID` do **not** show FK.
3. Solid edges to CUSTOMERS, PRODUCT MASTER (handle + SKU), and dashed edge to SHOPIFY_CHECKOUT.
4. SESSIONS edge is dashed with the grey label visible.

New entities (`CUSTOMERS`, `SHOPIFY_CHECKOUT`) are placed to the **right of ORDERS**. You may drag them for a cleaner “customer at centre” layout if desired.

---

## Changes applied to `Group1_ERD.drawio`

### 1. ORDERS PK/FK (your requested fixes)

| Field | Before | After | STTM / data rationale |
|-------|--------|-------|------------------------|
| `line_ID` | PK | PK | `Line: ID` is unique at line grain |
| `line_variant_ID` | Incorrectly marked FK | **Attribute only** | Not unique (~24k duplicates); not a join key |
| `line_product_ID` | Incorrectly marked FK | **Attribute only** | ~68% null; pipeline does not join on product ID |
| `line_product_handle` | Not FK | **FK → PRODUCT MASTER.handle** | Primary product join; 100% match when populated |
| `checkout_ID` | Missing | **FK → SHOPIFY_CHECKOUT** | Order-level; ~30–35% populated in export |
| `customer_ID` | FK (no target) | **FK → CUSTOMERS (derived)** | Required analytical join key |

### 2. New entities and edges

- **CUSTOMERS (derived)** — PK `customer_id`; edge from `ORDERS.customer_ID`
- **SHOPIFY_CHECKOUT (logical)** — PK `checkout_id`; **dashed** edge from `ORDERS.checkout_ID` (external Shopify object, not a project CSV)
- **ORDERS.line_product_handle → PRODUCT MASTER.handle** — solid FK edge (in addition to existing `line_SKU → variant_SKU`)

### 3. Conceptual / non-FK relationships

- **SESSIONS BY REFERRER → ORDERS** — edge restyled as **dashed/open arrow**; label added: *standalone (no order FK) — attribution only*
- **DISCOUNTS → ORDERS** — remains soft link via `Tags` (no hard FK in data); acceptable per README

---

## Entity-by-entity audit

### ORDERS (denormalized Shopify export)

| Check | Result |
|-------|--------|
| Dual PK (`ID` + `line_ID`) | **Valid** for one wide table mirroring export; README analytical model splits `orders` / `lines` — both views are consistent if you note grain in the slide |
| FK keys match STTM | **Yes** — `customer_id`, `checkout_id`, `line_product_handle`, `line_sku` |
| Non-FK attributes | **Yes** — `line_product_id`, `line_variant_id` correctly unmarked |
| UTM / browser columns inside ORDERS | **Correct** — order-level attribution fields; not the same as campaigns aggregate file |

### CUSTOMERS (derived)

| Check | Result |
|-------|--------|
| Exists in diagram | **Yes** (added) |
| PK | `customer_id` — matches `customers.parquet` / README |
| Relationship | Many orders → one customer |

### SHOPIFY_CHECKOUT (logical)

| Check | Result |
|-------|--------|
| Exists in diagram | **Yes** (added) |
| Populated in data | ~30–35% of orders have `Checkout ID` |
| Loaded to parquet | **No** in current pipeline — STTM still documents FK for completeness |
| Edge style | **Dashed** — signals optional / logical entity |

### PRODUCT MASTER

| Check | Result |
|-------|--------|
| Composite PK | `handle` + `variant_SKU` — matches `products_master` |
| Incoming FKs | From `ORDERS.line_product_handle`, `ORDERS.line_SKU`, Recharge item tables via SKU |
| Join quality | Handle join ~100% when populated; SKU join ~22% (legacy SKU drift) — diagram is still correct |

### DISCOUNTS

| Check | Result |
|-------|--------|
| PK | `name` (discount code string) |
| Link to orders | Via parsed `Tags` — **conceptual**, not enforceable FK |

### SESSIONS BY REFERRER (= campaigns / referrer aggregate)

| Check | Result |
|-------|--------|
| Standalone | **Yes** — file has no `order_id` or `customer_id` |
| Misleading FK edge | **Mitigated** — dashed + label; do not describe as FK in presentation |

### RECHARGE ORDERS

| Check | Result |
|-------|--------|
| PK | `recharge_order_id` |
| FK `shopify_order_id` → ORDERS | **Correct** — bridge to Shopify |
| FK `customer_id` | Points to Recharge customer namespace — **not** Shopify `customer_id` (DQ-11: IDs do not match) |

### ORDER ITEMS CHECKOUT / ORDER ITEMS RECURRING

| Check | Result |
|-------|--------|
| FK to RECHARGE ORDERS | **Correct** |
| FK to ORDERS via `shopify_order_id` | **Correct** |
| FK to PRODUCT MASTER via SKU / product fields | **Correct** |

### SUBSCRIBERS REACTIVATED / SUBSCRIPTIONS CHURNED

| Check | Result |
|-------|--------|
| FK to RECHARGE ORDERS | **Correct** |
| Churned → PRODUCT MASTER | **Correct** (product-level churn analysis) |

---

## Relationship inventory (post-fix)

```
CUSTOMERS (derived)  ←── ORDERS.customer_ID
SHOPIFY_CHECKOUT     ←── ORDERS.checkout_ID (dashed, optional)
PRODUCT MASTER       ←── ORDERS.line_product_handle
PRODUCT MASTER       ←── ORDERS.line_SKU
ORDERS               ←── RECHARGE ORDERS.shopify_order_id
ORDERS               ←── ORDER ITEMS CHECKOUT / RECURRING.shopify_order_id
RECHARGE ORDERS      ←── ORDER ITEMS CHECKOUT / RECURRING
RECHARGE ORDERS      ←── SUBSCRIBERS REACTIVATED / SUBSCRIPTIONS CHURNED
PRODUCT MASTER       ←── ORDER ITEMS *, SUBSCRIPTIONS CHURNED
ORDERS               ←── DISCOUNTS (conceptual, via tags)
SESSIONS BY REFERRER ⇢ ORDERS (conceptual attribution only, dashed)
```

---

## README §7 alignment note

README describes **9 source entities** with **Customer at centre** and separate **orders** / **lines** tables. The draw.io file uses a **single denormalized ORDERS** entity (all Shopify columns in one table). That is **not wrong** — it matches the raw export and the filled STTM — but for the mid-term slide you may want one sentence:

> *“Analytical pipeline normalizes to `orders.parquet` + `lines.parquet`; this ERD shows the source export shape.”*

Entity count is now **11 boxes** (9 data files + 2 logical/derived: CUSTOMERS, SHOPIFY_CHECKOUT).

---

## How to re-verify (automated)

```bash
python deliverables/parse_erd.py
```

Prints all entities, PK/FK fields per table, and relationship edges. Use together with the **Layout note** section above for visual checks in draw.io.

---

## Sign-off

| Reviewer action | Done |
|-----------------|------|
| Apply four ORDERS PK/FK corrections | Yes |
| Add missing FK targets (customer, checkout, handle) | Yes |
| Full diagram audit vs datasets + STTM | Yes (this document) |
| Label conceptual relationships | Yes |
