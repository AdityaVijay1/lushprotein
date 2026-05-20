"""
fix_encoding3.py -- aggressive clean-ASCII pass on all .py files.

For files that still contain non-UTF-8 bytes or high-codepoint characters,
decode the file with errors='replace', then map every non-ASCII codepoint
to a best-fit ASCII character, write back as pure UTF-8.
"""
import pathlib
import unicodedata

BASE = pathlib.Path(__file__).parent.parent
DIRS = [BASE / 'EDA', BASE / 'visualizations']

# Map non-ASCII Unicode codepoints -> ASCII string
# Handles any stragglers after byte-level fixes
CHAR_MAP = {
    '\u2014': '--',   # em dash
    '\u2013': '-',    # en dash
    '\u2012': '-',    # figure dash
    '\u2015': '--',   # horizontal bar
    '\u2550': '=',    # box double horizontal
    '\u2500': '-',    # box light horizontal
    '\u2501': '-',    # box heavy horizontal
    '\u2502': '|',    # box light vertical
    '\u2551': '|',    # box double vertical
    '\u2554': '+',    # box corner
    '\u2557': '+',
    '\u255a': '+',
    '\u255d': '+',
    '\u253c': '+',    # box cross
    '\u2022': '*',    # bullet
    '\u2019': "'",    # right single quote
    '\u2018': "'",    # left single quote
    '\u201c': '"',    # left double quote
    '\u201d': '"',    # right double quote
    '\u2026': '...',  # ellipsis
    '\u00d7': 'x',   # multiplication sign
    '\u00f7': '/',   # division sign
    '\u00b0': ' deg',# degree
    '\u00b7': '*',   # middle dot
    '\u00a0': ' ',   # non-breaking space
    '\u20ac': 'EUR', # euro sign (standalone)
    '\u2192': '->',  # right arrow
    '\u2190': '<-',  # left arrow
    '\u2191': '^',   # up arrow
    '\u2193': 'v',   # down arrow
    '\u2713': 'OK',  # check mark
    '\u2717': 'X',   # cross mark
    '\u00ae': '(R)', # registered
    '\u00a9': '(C)', # copyright
    '\u221e': 'inf', # infinity
    '\u2248': '~=',  # approx equal
    '\u2265': '>=',  # >=
    '\u2264': '<=',  # <=
    '\u00b1': '+-',  # plus-minus
    '\u00e2': 'a',   # a with circumflex (orphaned corruption artifact)
    '\ufffd': '',    # replacement character (bad byte)
    '\u0090': '',    # control character
    '\u0080': '',    # control character
    '\u0081': '',    # control character
    '\u008d': '',    # control character
    '\u008f': '',    # control character
    '\u009d': '',    # control character
}

def clean_line(line):
    result = []
    i = 0
    while i < len(line):
        c = line[i]
        if ord(c) <= 127:
            result.append(c)
        elif c in CHAR_MAP:
            result.append(CHAR_MAP[c])
        else:
            # Try unicode normalize to ASCII
            normalized = unicodedata.normalize('NFKD', c)
            ascii_part = normalized.encode('ascii', 'ignore').decode('ascii')
            if ascii_part:
                result.append(ascii_part)
            else:
                # Drop unknown high codepoints
                pass
        i += 1
    return ''.join(result)

total_fixed = 0
total_clean = 0

for d in DIRS:
    for f in sorted(d.glob('*.py')):
        if f.name in ('fix_encoding.py', 'fix_encoding2.py', 'fix_encoding3.py'):
            total_clean += 1
            continue

        # Read bytes, decode with replacement
        raw = f.read_bytes()
        try:
            text = raw.decode('utf-8', errors='replace')
        except Exception:
            text = raw.decode('latin-1', errors='replace')

        lines = text.splitlines(keepends=True)
        new_lines = [clean_line(l) for l in lines]
        new_text = ''.join(new_lines)

        # Also collapse runs of === or --- in pure separator comment lines
        # e.g. "# ============================================" is fine
        # But "# ===*===*===*" is already cleaned above

        if new_text != text:
            f.write_text(new_text, encoding='utf-8')
            total_fixed += 1
            print(f"  FIXED  {f.name}")
        else:
            total_clean += 1

print(f"\nTotal fixed: {total_fixed}  |  Already clean: {total_clean}")

# Final verification
print("\n=== FINAL NON-ASCII CHECK ===")
remaining = 0
for d in DIRS:
    for f in sorted(d.glob('*.py')):
        if f.name in ('fix_encoding.py', 'fix_encoding2.py', 'fix_encoding3.py'):
            continue
        txt = f.read_text(encoding='utf-8', errors='replace')
        bad = [(i+1, l) for i,l in enumerate(txt.splitlines()) if any(ord(c)>127 for c in l)]
        if bad:
            remaining += 1
            print(f"  STILL HAS ISSUES: {f.name} ({len(bad)} lines)")
            for ln, l in bad[:2]:
                print(f"    L{ln}: {l[:80]!r}")

if remaining == 0:
    print("  ALL FILES CLEAN -- no non-ASCII characters remain")
print("Done.")
