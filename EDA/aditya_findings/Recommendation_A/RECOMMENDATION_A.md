# Recommendation A — Stop Treating Your Best Customers Like Strangers

**Script:** `run_recommendation_a.py`  
**One sentence:** Tag your top 429 customers in Klaviyo, stop sending them the same 10%-off codes as everyone else.

---

## The problem (in plain English)

LushProtein sends the same promotions to everyone. But **429 customers (10%) generate 41% of true gross profit**. A blanket 10%-off sale costs **S$14K+ in GP** on those buyers alone — and they would have bought anyway.

Worse: **185 "loyal" customers (frequency D1) are not profit D1**. They reorder often but spend less per order (S$176 revenue vs S$588 for VIPs). Blanket promos subsidise the wrong people.

---

## What to do (3 steps)

### Step 1 — Export CRM tiers (done — ready for Klaviyo)

File: `outputs/klaviyo_crm_tiers.csv` (4,290 customers)

| Tier | Who | Count | % of GP | Promo policy |
|------|-----|-------|---------|--------------|
| **VIP** | Profit D1 AND Frequency D1 | **245** | **26%** | No site-wide % off. Early access, bundles, subscription. |
| **Profit_D1** | High spend, not frequent | **184** | **15%** | No blanket promo. Premium upsell, 1kg packs. |
| **Freq_D1** | Frequent, lower spend | **184** | **5%** | Replenishment emails only. Subscribe-and-save. |
| **Standard** | Everyone else | **3,677** | **54%** | Normal acquisition/win-back. |

### Step 2 — Change promo rules in Shopify + Klaviyo

- **Exclude VIP + Profit_D1** from site-wide discount codes
- Give VIPs **exclusive bundles** instead of % off
- Give Freq_D1 **replenishment reminders** at ~54 days (Clear) / ~35 days (Lean TMT)

### Step 3 — Measure

Track `$/unit` and `avg_margin_pct` by tier quarterly. If D1 margin drops after a campaign, the promo leaked.

---

## Proof (figures in `outputs/`)

### Figure 1: `fig_gp_by_decile_true.png`
D1 avg true GP = **S$326** vs D10 = **S$5** → **69× gap**

### Figure 2: `fig_d1_profit_vs_frequency.png`
Profit D1 and Frequency D1 are different segments — need different playbooks

### Figure 3: `fig_discount_erosion.png`
10% site-wide on D1 = **S$14K GP lost**; 15% = **S$21K**

### Figure 4: `fig_crm_tier_summary.png`
245 VIPs hold **26% of all GP** — tiny group, huge prize

### Figure 5: `fig_margin_by_tier.png`
VIPs earn **65% margin** vs 40% proxy assumption

---

## Size of prize

| Lever | Conservative yield |
|-------|-------------------|
| Stop 10% leakage on D1 base | **S$14K GP protected/yr** |
| VIP retention (5% churn prevented on 245) | **S$4.4K GP** |
| **Total Rec A** | **~S$18–20K GP** |

**Execution:** 2–4 weeks. Export CSV → Klaviyo tags. No new SKUs.

---

## Regenerate

```bash
python EDA/aditya_findings/Recommendation_A/run_recommendation_a.py
```
