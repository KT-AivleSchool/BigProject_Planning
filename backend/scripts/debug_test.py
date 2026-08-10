import os
import sys
import json
import pandas as pd
import numpy as np
import geopandas as gpd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.gam4_site_select import (
    load_exclusions, _read_parcels, REGION_DATA_DIR, STEP1_OUTPUT_DIR,
    make_loader, load_weight_set, domain_prefix
)
from app.services import gam4_spatial_ops as S
from app.services import gam4_facility_params as FP

domain = "흡연"
prefix = domain_prefix(domain)
loader, report = make_loader(domain)
reviewed = json.load(open(os.path.join(STEP1_OUTPUT_DIR, f"{prefix}_audit_result_reviewed.json"), encoding="utf-8"))

cpath = "data_임시/step3_output/흡연_후보_지적도필지.gpkg"
parcels = _read_parcels(cpath, None)

pts = S.points_in_parcels(parcels, spacing=5, max_per_parcel=0)
for c in ("PNU", "JIBUN", "지목", "면적", "내접폭", "법정동코드",
          "국유_건수", "국유_지분면적", "국유_지분율", "국유_지번일치"):
    if c in parcels.columns:
        pts[c] = parcels[c].to_numpy()[pts["parcel_idx"].to_numpy()]

union, excl_layers, excl_rows = load_exclusions(reviewed, loader)
keep_base = S.filter_outside(pts, union)

min_width = 2.0
if min_width is not None and "내접폭" in pts.columns:
    keep_base = keep_base & (pts["내접폭"].to_numpy() >= min_width)

if "국유_건수" in pts.columns:
    is_public = (pts["국유_건수"] > 0).to_numpy()
else:
    is_public = np.zeros(len(pts), dtype=bool)
    
public_survived = (is_public & keep_base).sum()

print("DEBUG:")
print("len(pts) =", len(pts))
print("min_width =", min_width)
print("is_public.sum() =", is_public.sum())
print("keep_base.sum() =", keep_base.sum())
print("(is_public & keep_base).sum() =", public_survived)
