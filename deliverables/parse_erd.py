"""Parse Group1_ERD.drawio for audit."""
import re
from pathlib import Path

xml = Path(__file__).resolve().parent.parent / "Group1_ERD.drawio"
text = xml.read_text(encoding="utf-8")

tables = re.findall(
    r'id="([^"]+)"[^>]*style="[^"]*shape=table[^"]*"[^>]*value="([^"]+)"',
    text,
)
table_ids = {tid: name for tid, name in tables}

cells = re.findall(
    r'<mxCell id="([^"]+)" parent="([^"]+)"[^>]*value="([^"]*)" vertex="1"',
    text,
)
by_parent = {}
for cid, parent, val in cells:
    by_parent.setdefault(parent, []).append((cid, val))


def descendants(root):
    out = []
    for cid, val in by_parent.get(root, []):
        out.append((cid, val))
        out.extend(descendants(cid))
    return out


def get_keys(table_id):
    desc = descendants(table_id)
    keys = []
    i = 0
    while i < len(desc):
        cid, val = desc[i]
        if val in ("PK", "FK"):
            field = desc[i + 1][1] if i + 1 < len(desc) else "?"
            keys.append((val, field, cid))
            i += 2
        else:
            i += 1
    return keys


print("=== ENTITIES ===")
for tid, name in tables:
    print(f"  {name}")

print("\n=== PK/FK BY ENTITY ===")
for tid, name in tables:
    keys = get_keys(tid)
    if keys:
        print(f"\n--- {name} ---")
        for k, f, _ in keys:
            print(f"  {k}: {f}")

# Resolve cell to entity name
cell_to_entity = {}
cell_to_field = {}
for tid, tname in tables:
    for cid, val in descendants(tid):
        cell_to_entity[cid] = tname
        if val and val not in ("PK", "FK", ""):
            cell_to_field[cid] = val

print("\n=== RELATIONSHIPS (edges) ===")
edges = re.findall(
    r'edge="1"[^>]*source="([^"]+)"[^>]*target="([^"]+)"',
    text,
)
for src, tgt in edges:
    se = cell_to_entity.get(src, "?")
    te = cell_to_entity.get(tgt, "?")
    sf = cell_to_field.get(src, src[:12])
    tf = cell_to_field.get(tgt, tgt[:12])
    print(f"  {se} [{sf}] -> {te} [{tf}]")
