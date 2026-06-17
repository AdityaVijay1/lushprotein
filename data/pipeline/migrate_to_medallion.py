"""
migrate_to_medallion.py — One-time (idempotent) migration to Medallion layout.

Moves existing data from legacy EDA/ paths into data/{bronze,silver,gold}/ and
creates directory junctions so all existing scripts keep working.

Run once:
    python data/pipeline/migrate_to_medallion.py

Safe to re-run — skips steps already completed.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
EDA = BASE / "EDA"
sys.path.insert(0, str(EDA))

import importlib.util

spec = importlib.util.spec_from_file_location("lp_config", EDA / "00_config.py")
cfg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cfg)

SILVER = cfg.SILVER_DIR
GOLD = cfg.GOLD_DIR
GOLD_REF = cfg.GOLD_REFERENCE_DIR
GOLD_DECILE = cfg.GOLD_ANALYTICS_DECILE
GOLD_CATEGORY = cfg.GOLD_ANALYTICS_CATEGORY
GOLD_FINDINGS = cfg.GOLD_ANALYTICS_FINDINGS
BRONZE_SUPP = cfg.BRONZE_SUPPLEMENTAL_DIR

LEGACY_SILVER = cfg.LEGACY_SILVER_JUNCTION
LEGACY_GOLD = cfg.LEGACY_GOLD_JUNCTION
LEGACY_DECILE = cfg.LEGACY_DECILE_JUNCTION
LEGACY_CATEGORY = cfg.LEGACY_CATEGORY_JUNCTION

FINDINGS_MODULES = [
    "margin_analysis",
    "pitch_analysis",
    "Recommendation_A",
    "Recommendation_B",
    "recommendation_systems",
    "rec_f_g_validation",
]

COGS_SRC = EDA / "aditya_findings" / "20260616-COGS_Data_Request_LushProtein (1).xlsx"
COGS_DST_DIR = BRONZE_SUPP / "cogs"


def is_junction(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        return path.is_symlink() or (path.lstat().st_file_attributes & 0x400) != 0  # FILE_ATTRIBUTE_REPARSE_POINT
    except (OSError, AttributeError):
        return path.is_symlink()


def create_junction(link: Path, target: Path) -> bool:
    """Create Windows directory junction (or symlink fallback)."""
    target = target.resolve()
    if link.exists():
        if is_junction(link) or link.is_symlink():
            print(f"  [skip] junction exists: {link.name}")
            return True
        print(f"  [warn] {link} exists and is not a junction — manual review needed")
        return False

    link.parent.mkdir(parents=True, exist_ok=True)
    # Windows junction via cmd
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(target)],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"  [ok] junction {link.name} -> {target}")
        return True

    # Fallback: symlink
    try:
        link.symlink_to(target, target_is_directory=True)
        print(f"  [ok] symlink {link.name} -> {target}")
        return True
    except OSError as e:
        print(f"  [fail] could not link {link}: {e}")
        return False


def move_contents(src: Path, dst: Path, exclude_dirs: set[str] | None = None) -> int:
    """Move all files/subdirs from src to dst. Returns count moved."""
    if not src.exists() or is_junction(src):
        return 0
    exclude_dirs = exclude_dirs or set()
    moved = 0
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if item.name in exclude_dirs:
            continue
        dest = dst / item.name
        if dest.exists():
            continue
        shutil.move(str(item), str(dest))
        moved += 1
    return moved


def migrate_silver() -> None:
    print("\n[1] Silver: EDA/outputs -> data/silver")
    legacy = LEGACY_SILVER
    if legacy.exists() and not is_junction(legacy):
        n = move_contents(legacy, SILVER)
        print(f"  Moved {n} items to {SILVER}")
        # Remove empty legacy dir if possible
        try:
            if legacy.exists() and not any(legacy.iterdir()):
                legacy.rmdir()
        except OSError:
            pass
    create_junction(legacy, SILVER)


def migrate_gold() -> None:
    print("\n[2] Gold: EDA/outputs_finals -> data/gold")
    legacy = LEGACY_GOLD
    if legacy.exists() and not is_junction(legacy):
        # Move do_not_use_these to reference first
        dnu = legacy / "do_not_use_these"
        if dnu.exists():
            GOLD_REF.mkdir(parents=True, exist_ok=True)
            move_contents(dnu, GOLD_REF)
            try:
                if dnu.exists() and not any(dnu.iterdir()):
                    dnu.rmdir()
            except OSError:
                pass
        n = move_contents(legacy, GOLD, exclude_dirs={"do_not_use_these"})
        print(f"  Moved {n} items to {GOLD}")
        try:
            if legacy.exists() and not any(legacy.iterdir()):
                legacy.rmdir()
        except OSError:
            pass
    create_junction(legacy, GOLD)


def migrate_decile_analytics() -> None:
    print("\n[3] Gold analytics: decile")
    legacy = LEGACY_DECILE
    if legacy.exists() and not is_junction(legacy):
        n = move_contents(legacy, GOLD_DECILE)
        print(f"  Moved {n} items to {GOLD_DECILE}")
        try:
            if legacy.exists() and not any(legacy.iterdir()):
                legacy.rmdir()
        except OSError:
            pass
    create_junction(legacy, GOLD_DECILE)


def migrate_category_analytics() -> None:
    print("\n[4] Gold analytics: category")
    legacy = LEGACY_CATEGORY
    if legacy.exists() and not is_junction(legacy):
        n = move_contents(legacy, GOLD_CATEGORY)
        print(f"  Moved {n} items to {GOLD_CATEGORY}")
        try:
            if legacy.exists() and not any(legacy.iterdir()):
                legacy.rmdir()
        except OSError:
            pass
    create_junction(legacy, GOLD_CATEGORY)


def migrate_findings_analytics() -> None:
    print("\n[5] Gold analytics: findings")
    for mod in FINDINGS_MODULES:
        src = EDA / "aditya_findings" / mod / "outputs"
        dst = GOLD_FINDINGS / mod
        if src.exists() and not is_junction(src):
            n = move_contents(src, dst)
            if n:
                print(f"  {mod}: moved {n} items")
            try:
                if src.exists() and not any(src.iterdir()):
                    src.rmdir()
            except OSError:
                pass
        if not src.exists() or is_junction(src):
            create_junction(src, dst)
        else:
            dst.mkdir(parents=True, exist_ok=True)
            create_junction(src, dst)


def copy_bronze_supplemental() -> None:
    print("\n[6] Bronze supplemental: COGS copy")
    COGS_DST_DIR.mkdir(parents=True, exist_ok=True)
    if COGS_SRC.exists():
        dst = COGS_DST_DIR / COGS_SRC.name
        if not dst.exists():
            shutil.copy2(COGS_SRC, dst)
            print(f"  Copied COGS to {dst}")
        else:
            print("  [skip] COGS already in bronze/supplemental")
    else:
        print("  [warn] COGS source not found — skip")


def write_bronze_manifest() -> None:
    print("\n[7] Bronze manifest")
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "architecture": "medallion",
        "sources": [],
    }
    sources = [
        ("orders", cfg.BRONZE_ORDERS_DIR, "1_*.xlsx"),
        ("products", cfg.BRONZE_PRODUCTS_DIR, "2_1.products_master_20260505.xlsx"),
        ("discounts", cfg.BRONZE_DISCOUNTS_DIR, "3_1.discounts_export*.csv"),
        ("recharge", cfg.BRONZE_RECHARGE_DIR, "5_*.xlsx"),
    ]
    for name, folder, pattern in sources:
        if folder.exists():
            if "*" in pattern:
                files = sorted(folder.glob(pattern))
            else:
                files = [folder / pattern] if (folder / pattern).exists() else []
            manifest["sources"].append({
                "name": name,
                "path": str(folder.relative_to(BASE)),
                "files": [f.name for f in files],
                "exists": len(files) > 0,
            })
    out = cfg.BRONZE_DIR / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"  Wrote {out}")


def write_legacy_readmes() -> None:
    """Stub README at legacy paths if junction — points to medallion."""
    stubs = {
        LEGACY_SILVER: SILVER,
        LEGACY_GOLD: GOLD,
        LEGACY_DECILE: GOLD_DECILE,
        LEGACY_CATEGORY: GOLD_CATEGORY,
    }
    for link, target in stubs.items():
        if link.exists() and is_junction(link):
            readme = link / "README_MEDALLION.md"
            if not readme.exists():
                readme.write_text(
                    f"# Legacy path — Medallion migration\n\n"
                    f"This directory is a junction to `{target.relative_to(BASE)}`.\n\n"
                    f"See `data/README.md` for the medallion architecture.\n",
                    encoding="utf-8",
                )


def main() -> None:
    print("=" * 70)
    print("MEDALLION MIGRATION")
    print("=" * 70)
    print(f"Project: {BASE}")

    migrate_silver()
    migrate_gold()
    migrate_decile_analytics()
    migrate_category_analytics()
    migrate_findings_analytics()
    copy_bronze_supplemental()
    write_bronze_manifest()
    write_legacy_readmes()

    print("\n" + "=" * 70)
    print("MIGRATION COMPLETE")
    print("=" * 70)
    print("Canonical paths:")
    print(f"  Silver:   {SILVER}")
    print(f"  Gold:     {GOLD}")
    print(f"  Analytics: {cfg.GOLD_ANALYTICS_DIR}")
    print("\nLegacy junctions preserved at EDA/outputs and EDA/outputs_finals")


if __name__ == "__main__":
    main()
