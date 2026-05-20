import sys, importlib.util, pathlib
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('cfg', '00_config.py')
cfg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cfg)
import pandas as pd
OUT = pathlib.Path(cfg.OUTPUT_DIR)
orders = pd.read_parquet(OUT / 'orders.parquet')

sg_ids  = set(orders[orders.store=='SG'].customer_id.unique())
my_ids  = set(orders[orders.store=='MY'].customer_id.unique())
hk_ids  = set(orders[orders.store=='HK'].customer_id.unique())
all_ids = set(orders.customer_id.unique())
overlap = sg_ids & my_ids

print("SG unique customers      :", len(sg_ids))
print("MY unique customers      :", len(my_ids))
print("Sum (naive add)          :", len(sg_ids) + len(my_ids), "<-- double-counts cross-market buyers")
print("Overlap (bought from both SG and MY):", len(overlap))
print("Actual combined (union)  :", len(all_ids))
print()
print("Union formula: SG + MY - Overlap")
print(f"  {len(sg_ids)} + {len(my_ids)} - {len(overlap)} = {len(sg_ids)+len(my_ids)-len(overlap)}")
