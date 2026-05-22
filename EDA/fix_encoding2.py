"""
fix_encoding2.py -- byte-level cleanup of all Python scripts.

Strategy: Read each file as raw bytes, apply byte-pattern replacements
for known UTF-8 encoded Unicode characters that should be plain ASCII,
then write back as UTF-8.
"""
import pathlib

BASE = pathlib.Path(__file__).parent.parent

# Byte-level replacements: (bytes_to_find, bytes_to_replace_with)
# Ordered longest match first.
BYTE_RULES = [
    # UTF-8 BOM
    (b'\xef\xbb\xbf', b''),
    # Em dash (U+2014 = E2 80 94)
    (b'\xe2\x80\x94', b'--'),
    # En dash (U+2013 = E2 80 93)
    (b'\xe2\x80\x93', b'-'),
    # Box drawing double horizontal (U+2550 = E2 95 90)
    (b'\xe2\x95\x90', b'='),
    # Box drawing light horizontal (U+2500 = E2 94 80)
    (b'\xe2\x94\x80', b'-'),
    # Box drawing vertical (U+2502 = E2 94 82)
    (b'\xe2\x94\x82', b'|'),
    # Box drawing double vertical (U+2551 = E2 95 91)
    (b'\xe2\x95\x91', b'|'),
    # Bullet (U+2022 = E2 80 A2)
    (b'\xe2\x80\xa2', b'*'),
    # Left double quote (U+201C = E2 80 9C)
    (b'\xe2\x80\x9c', b'"'),
    # Right double quote (U+201D = E2 80 9D)
    (b'\xe2\x80\x9d', b'"'),
    # Left single quote (U+2018 = E2 80 98)
    (b'\xe2\x80\x98', b"'"),
    # Right single quote / apostrophe (U+2019 = E2 80 99)
    (b'\xe2\x80\x99', b"'"),
    # Multiplication sign (U+00D7 = C3 97)
    (b'\xc3\x97', b'x'),
    # Division sign (U+00F7 = C3 B7)
    (b'\xc3\xb7', b'/'),
    # Latin small letter a with circumflex (U+00E2 = C3 A2)
    # -- only in context where it appears as corruption artifact;
    # but this could be intentional, so skip standalone \xc3\xa2
    # Middle dot (U+00B7 = C2 B7)
    (b'\xc2\xb7', b'*'),
    # Non-breaking space (U+00A0 = C2 A0)
    (b'\xc2\xa0', b' '),
    # Box drawings double up and right (U+2554 = E2 95 94)
    (b'\xe2\x95\x94', b'+'),
    # Box drawings double up and left (U+2557 = E2 95\x97)
    (b'\xe2\x95\x97', b'+'),
    # Box drawings double down and right (U+255A = E2 95 9A)
    (b'\xe2\x95\x9a', b'+'),
    # Box drawings double down and left (U+255D = E2 95 9D)
    (b'\xe2\x95\x9d', b'+'),
    # Right arrow (U+2192 = E2 86 92)
    (b'\xe2\x86\x92', b'->'),
    # Left arrow (U+2190 = E2 86 90)
    (b'\xe2\x86\x90', b'<-'),
    # Up arrow (U+2191 = E2 86 91)
    (b'\xe2\x86\x91', b'^'),
    # Down arrow (U+2193 = E2 86 93)
    (b'\xe2\x86\x93', b'v'),
    # Check mark (U+2713 = E2 9C 93)
    (b'\xe2\x9c\x93', b'OK'),
    # Cross mark (U+2717 = E2 9C 97)
    (b'\xe2\x9c\x97', b'X'),
    # Degree sign (U+00B0 = C2 B0)
    (b'\xc2\xb0', b' deg'),
    # Registered (U+00AE = C2 AE)
    (b'\xc2\xae', b'(R)'),
    # Copyright (U+00A9 = C2 A9)
    (b'\xc2\xa9', b'(C)'),
    # Infinity (U+221E = E2 88 9E)
    (b'\xe2\x88\x9e', b'inf'),
    # Approximately equal (U+2248 = E2 89 88)
    (b'\xe2\x89\x88', b'~='),
    # Greater-than or equal (U+2265 = E2 89 A5)
    (b'\xe2\x89\xa5', b'>='),
    # Less-than or equal (U+2264 = E2 89 A4)
    (b'\xe2\x89\xa4', b'<='),
    # Ellipsis (U+2026 = E2 80 A6)
    (b'\xe2\x80\xa6', b'...'),
]

DIRS = [BASE / 'EDA', BASE / 'visualizations']

total_fixed = 0
total_clean = 0

for d in DIRS:
    for f in sorted(d.glob('*.py')):
        original = f.read_bytes()
        data = original
        for bad, good in BYTE_RULES:
            data = data.replace(bad, good)
        if data != original:
            f.write_bytes(data)
            n_replacements = sum(original.count(bad) for bad, _ in BYTE_RULES)
            print(f"  FIXED  {f.name}  ({n_replacements} byte-sequences replaced)")
            total_fixed += 1
        else:
            total_clean += 1

print(f"\nTotal fixed: {total_fixed}  |  Already clean: {total_clean}")
print("\nRunning post-fix non-ASCII check...")
for d in DIRS:
    for f in sorted(d.glob('*.py')):
        try:
            txt = f.read_bytes().decode('utf-8')
            bad_lines = [(i+1, l) for i, l in enumerate(txt.splitlines())
                         if any(ord(c) > 127 for c in l)]
            if bad_lines:
                print(f"  REMAINING: {f.name} has {len(bad_lines)} lines with non-ASCII")
                for ln, l in bad_lines[:2]:
                    print(f"    L{ln}: {l[:80]!r}")
        except UnicodeDecodeError as e:
            print(f"  DECODE ERROR: {f.name}: {e}")
print("Done.")
