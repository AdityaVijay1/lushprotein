# Part A Visualization Guide — Final Report PDF

Insert these figures when converting `Final_report.md` to PDF. All Part A charts are in `EDA/report_details/charts/`.

## Required figures (generated)

| Order in PDF | File | Insert after section | Size suggestion |
|--------------|------|----------------------|---------------|
| 1 | `part_a_cohort_funnel.png` | §2.5 Final Revisions | Full width |
| 2 | `part_a_order_funnel.png` | §2.5 (below cohort funnel) | Full width |
| 3 | `part_a_revenue_distribution.png` | §2.2.1 Order Revenue | Full width, side-by-side panels |
| 4 | `part_a_one_time_buyer_rate.png` | §2.2.2 Orders per Customer | Half width |
| 5 | `part_a_missing_values.png` | §2.2.5 Missing Values | Full width |
| 6 | `part_a_filter_layers.png` | §2.3 (end of discrepancies) | Full width |

## Screenshots to capture manually

| Item | Source | Section |
|------|--------|---------|
| Manifest row counts | Open `EDA/outputs_finals/manifest.json` | §2.6 |
| Build script log | Run `python EDA/13_build_finals_datasets.py`, screenshot console | §2.6 |
| Margin enrichment | `EDA/outputs_finals/margin_enrichment_summary.json` | §2.9 |

## Optional supporting figures (existing EDA)

| File | Use |
|------|-----|
| `EDA/outputs_finals/decile_overlap_heatmap.png` | Appendix — decile exclusions (4,290 pool) |
| `aditya_findings/margin_analysis/outputs/fig_proxy_vs_true_gp.png` | §2.9 COGS update |
| `EDA/outputs/equal_revenue_slicing.png` | §2.2.1 revenue skew context |

## Suggested Part A page layout (~10 pages)

1. **§2.1** Introduction + temporal table (no chart required)
2. **§2.2** Summary stats + **Fig A-2, A-3, A-4**
3. **§2.3** Data issues §3.1–3.6 (tables only)
4. **§2.3** Data issues §3.7–3.12 + **Fig A-5**
5. **§2.4** LTV definitions
6. **§2.5** **FINAL REVISIONS banner** + **Fig A-1, A-7**
7. **§2.6–2.7** DQ + LP tables + manifest screenshot
8. **§2.8** Layer 0 & 3
9. **§2.9** COGS enrichment + optional proxy vs true GP
10. **§2.10–2.11** Before/after table + limitations

## Regenerate

```bash
python EDA/report_details/build_part_a_charts.py
```
