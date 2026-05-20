"""
fix_encoding.py -- strip BOM and replace corrupted UTF-8 sequences
with clean ASCII equivalents across all .py files in EDA/ and visualizations/.
"""
import os
import pathlib

BASE = pathlib.Path(__file__).parent.parent

# Corrupted UTF-8 sequences (bytes mis-decoded as Latin-1/Windows-1252)
# and their clean ASCII replacements.
# Order matters: longer patterns first.
REPLACEMENTS = [
    # Box-drawing separators (double horizontal: U+2550 = E2 95 90)
    # show as "â*\x90" when mis-decoded
    ("\u00e2\u0095\u0090", "="),        # â*\x90  -> =  (double horiz)
    # Box-drawing light horizontal (U+2500 = E2 94 80)
    ("\u00e2\u0094\u0080", "-"),        # â"€    -> -
    # Box-drawing vertical (U+2502 = E2 94 82)
    ("\u00e2\u0094\u0082", "|"),        # â"‚    -> |
    # Em-dash (U+2014 = E2 80 94) corrupted
    ("\u00e2\u0080\u0094", "--"),       # â€"    -> --
    # En-dash (U+2013 = E2 80 93) corrupted
    ("\u00e2\u0080\u0093", "-"),        # â€"    -> -
    # Bullet (U+2022 = E2 80 A2) corrupted
    ("\u00e2\u0080\u00a2", "*"),        # â€¢    -> *
    # Left double quote (U+201C = E2 80 9C) corrupted
    ("\u00e2\u0080\u009c", '"'),        # â€œ    -> "
    # Right double quote (U+201D = E2 80 9D) corrupted
    ("\u00e2\u0080\u009d", '"'),        # â€    -> "
    # Left single quote (U+2018 = E2 80 98) corrupted
    ("\u00e2\u0080\u0098", "'"),        # â€˜    -> '
    # Right single quote (U+2019 = E2 80 99) corrupted
    ("\u00e2\u0080\u0099", "'"),        # â€™    -> '
    # Multiplication sign (U+00D7 = C3 97) corrupted
    ("\u00c3\u0097", "x"),              # Ã--    -> x
    # Euro sign misused as quote (U+20AC) - only in corrupted sequences
    # Already handled above via em-dash pattern
]

# BOM character
BOM = "\ufeff"

DIRS = [BASE / "EDA", BASE / "visualizations"]

changed = []
skipped = []

for d in DIRS:
    for f in sorted(d.glob("*.py")):
        try:
            original = f.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            skipped.append(f"{f.name}: read error {e}")
            continue

        text = original

        # Remove BOM
        if text.startswith(BOM):
            text = text[len(BOM):]

        # Apply all replacements
        for bad, good in REPLACEMENTS:
            text = text.replace(bad, good)

        # Collapse runs of === or --- only in comment/separator lines
        # e.g. "# ========================================" is fine as-is
        # Do NOT collapse inside strings -- the replace above is character-level

        if text != original:
            f.write_text(text, encoding="utf-8")
            # Count replaced chars for reporting
            n = sum(original.count(bad) for bad, _ in REPLACEMENTS)
            n += original.startswith(BOM)
            changed.append(f"  FIXED  {f.name} ({n} replacements)")
        else:
            skipped.append(f"  clean  {f.name}")

print("=== ENCODING FIX REPORT ===\n")
print("Files modified:")
for s in changed:
    print(s)
if not changed:
    print("  (none)")
print()
print("Files already clean:")
for s in skipped:
    print(s)
print(f"\nTotal fixed: {len(changed)}  |  Already clean: {len(skipped)}")
