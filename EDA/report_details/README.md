# LushProtein Final Report — Document Index

All submission materials for the ISSS603 final report live in this folder.

## Files

| File | Description |
|------|-------------|
| `Final_report.md` | **Main deliverable** — Part A (data cleaning) + Part B (Solution 2 recommender) |
| `mid_term_report.md` | Mid-term data quality report (source for Part A carry-forward) |
| `presentation_slides.md` | Final presentation slide content (both solutions) |
| `1. Mid-term Report - Group 1 LushProtein SMU X (1).pdf` | Mid-term PDF submission |
| `xLP.pdf` | Final presentation deck (PDF) |
| `build_part_a_charts.py` | Script to regenerate Part A visualisations |
| `part_a_visualization_guide.md` | Where to insert each Part A figure in the PDF |

## Charts

Generated Part A figures: `charts/`

```
python EDA/report_details/build_part_a_charts.py
```

Part B figures remain in: `EDA/aditya_findings/outputs/charts/`

## Data pipeline (finals)

```
python EDA/13_build_finals_datasets.py
python EDA/aditya_findings/enrich_finals_with_margin.py
```

Authoritative counts: `EDA/outputs_finals/manifest.json`
