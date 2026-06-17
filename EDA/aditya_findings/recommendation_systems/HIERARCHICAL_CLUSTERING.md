# Hierarchical Clustering — Does It Make Sense for LushProtein?

**Script:** `hierarchical_clustering.py`

---

## Short answer

**Yes, as a diagnostic and segmentation tool — not as a primary recommender.**

Clustering groups customers by **what they buy and how much they spend**. For LP, it confirms what decile analysis already shows: a small premium core and a large casual Clear-buyer mass. Use it to **validate CRM tiers** and **design segment-specific playbooks**, not to replace the four recommenders.

---

## Method

- **Features:** Spend per category (Clear, Lean, Collagen, Accessories, Soy, Other) + orders + revenue + true GP
- **Algorithm:** Ward hierarchical clustering, k=5 clusters
- **Sample:** 500 customers for dendrogram viz; full 4,290 for cluster assignment

---

## Five clusters found

| Cluster | N | Avg GP | Profile |
|---------|---|--------|---------|
| **Premium_Other** (whales) | 16 | **S$1,340** | High spend, diverse categories |
| **Premium_Other** (core) | 368 | **S$232** | Multi-category, above-median GP |
| **Frequent_Soy** | 33 | S$201 | Niche loyalists |
| **Casual_Clear** | 3,712 | **S$55** | Single-category Clear buyers — largest group |
| **Casual_Accessories** | 161 | S$154 | Shaker-first, low protein attach |

---

## Why it helps

1. **Confirms Rec A:** Premium clusters = 9% of customers, ~40%+ of GP → protect them
2. **Confirms Rec B:** Casual_Clear (86% of pool) = cross-sell opportunity — they only buy Clear
3. **Validates tiering:** Clusters map roughly to VIP / Profit D1 / Standard

---

## Why it does NOT replace recommenders

| Limitation | Impact |
|------------|--------|
| Clusters are **static** (snapshot) | Don't tell you *what to recommend next* |
| **Casual_Clear dominates** (86%) | One-size-fits-all cluster email = same as blanket promo |
| Clusters lack **order sequence** | Can't power "after order 2, send Lean" |
| **Cold start** | New customer has no cluster until 1st purchase |

**Use clustering for:** Segment discovery, appendix charts, founder Q&A  
**Use recommenders for:** Actual product suggestions in emails and PDP

---

## Charts

| File | Use |
|------|-----|
| `fig_dendrogram_sample.png` | Appendix — shows customer similarity structure |
| `fig_cluster_heatmap.png` | Slide — category penetration by cluster |
| `fig_gp_by_cluster.png` | Slide — GP concentration in premium clusters |

---

## Regenerate

```bash
python EDA/aditya_findings/recommendation_systems/hierarchical_clustering.py
```
