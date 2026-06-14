# Margin Data Assessment

Assessment: **Usable with caveats**

- Total line revenue coverage with high-confidence cost: 31.6%
- Non-null SKU revenue coverage with high-confidence cost: 73.8%
- Core hero category revenue coverage (Lean, Clear, Collagen): 85.2%
- Top 20 SKU/title rows with any cost coverage: 7 / 20
- Product master cost rows: 58 / 167

Interpretation: Product master `Cost per item` is the best available internal cost source, and joining against both `Variant SKU` and `Variant Barcode` materially improves coverage. However, margin should be treated as an estimate because cost currency/effective date is not explicitly validated here, many historical lines lack usable SKU keys, and some high-revenue missing rows are barcode formatting or legacy product issues.
