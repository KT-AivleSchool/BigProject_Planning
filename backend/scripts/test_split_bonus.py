import os
import sys
import json
import time
import pandas as pd
import numpy as np
import geopandas as gpd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.gam4_site_select import (
    load_exclusions, _read_parcels, REGION_DATA_DIR, STEP1_OUTPUT_DIR, STEP3_OUTPUT_DIR,
    make_loader, load_weight_set, domain_prefix, score_candidates, build_demand_grid,
    select_mclp, check_consistency
)
from app.services import gam4_spatial_ops as S
from app.services import gam2_weight_model as W
from app.services import gam4_facility_params as FP

def run_split_experiment():
    domain = "흡연"
    prefix = domain_prefix(domain)
    loader, report = make_loader(domain)
    reviewed_path = os.path.join(STEP1_OUTPUT_DIR, f"{prefix}_audit_result_reviewed.json")
    if not os.path.exists(reviewed_path):
        print(f"Error: {reviewed_path} not found.")
        return
    with open(reviewed_path, "r", encoding="utf-8") as f:
        reviewed = json.load(f)
    
    ws = load_weight_set(domain)
    
    facility = (reviewed.get("facility_inference") or {}).get("facility", domain)
    fp = {k: v[2] for k, v in FP.PARAM_SPEC.items()}
    try:
        rec = FP.judge(facility)
        fp.update(rec.get("params", {}))
    except Exception:
        pass
        
    min_width = fp["설치_소요_폭_m"]
    
    cpath = os.path.join(STEP3_OUTPUT_DIR, f"{domain}_후보_지적도필지.gpkg")
    parcels = _read_parcels(cpath, None)
    pts = S.points_in_parcels(parcels, spacing=5, max_per_parcel=0)
    
    # ---------------------------------------------------------
    # Split National vs City logic
    # ---------------------------------------------------------
    print("Splitting National vs City ownership...")
    df_all = pd.read_csv('data_임시/region_data/국유부동산_위경도_v2_통합.csv')
    gdf_all = gpd.GeoDataFrame(df_all, geometry=gpd.points_from_xy(df_all['경도'], df_all['위도']), crs='EPSG:4326')
    gdf_all = gdf_all.to_crs(S.WORK_CRS)
    
    gdf_nat = gdf_all.iloc[:2486].copy()
    gdf_city = gdf_all.iloc[2486:].copy()
    
    parcels_poly = gpd.read_file(cpath, layer='parcels')
    nat_joined = gpd.sjoin(parcels_poly, gdf_nat, how='inner', predicate='intersects')
    city_joined = gpd.sjoin(parcels_poly, gdf_city, how='inner', predicate='intersects')
    
    nat_pnu = set(nat_joined['PNU'])
    city_pnu = set(city_joined['PNU'])
    
    pts['PNU'] = parcels['PNU'].to_numpy()[pts['parcel_idx'].to_numpy()]
    is_national = pts['PNU'].isin(nat_pnu).to_numpy()
    is_city = pts['PNU'].isin(city_pnu).to_numpy()
    
    # Add inner width for filtering
    if "내접폭" in parcels.columns:
        pts["내접폭"] = parcels["내접폭"].to_numpy()[pts["parcel_idx"].to_numpy()]
        
    inds = W.define_indicators(reviewed, report)
    W.attach_layers(inds, loader)
    check_consistency(ws, inds)
    
    from app.config import ADM_DONG_SHP
    admin_gdf = None
    if any(i["kind"] == "admin" for i in inds):
        if ADM_DONG_SHP and os.path.exists(ADM_DONG_SHP):
            admin_gdf = gpd.read_file(ADM_DONG_SHP).to_crs(W.WORK_CRS)
            
    score_base, norm, mat = score_candidates(pts, inds, ws, admin_gdf=admin_gdf)
    union, excl_layers, excl_rows = load_exclusions(reviewed, loader)
    keep_base = S.filter_outside(pts, union)
    
    if min_width is not None and "내접폭" in pts.columns:
        keep_base = keep_base & (pts["내접폭"].to_numpy() >= min_width)
        
    dgrid = build_demand_grid(cpath, parcels, 10)
    dscore_base, _, _ = score_candidates(dgrid, inds, ws, admin_gdf=admin_gdf, diag=False)
    
    scenarios = [
        {"name": "Scenario 1: 국유지만 (National Only)", "mask": is_national},
        {"name": "Scenario 2: 국유지 + 시유지 (National + City)", "mask": is_national | is_city}
    ]
    
    for sc in scenarios:
        print(f"\n==================================================")
        print(f" {sc['name']}")
        print(f"==================================================")
        is_public = sc["mask"]
        survived = (is_public & keep_base).sum()
        print(f" - 배제 필터 통과한 유효 공공부지 수: {survived}개")
        
        bonus_list = [0.0, 0.2, 0.4]
        results = []
        for b in bonus_list:
            score = score_base.copy()
            if b > 0:
                score[is_public] += b
            dscore = dscore_base.copy()
            
            sel = select_mclp(pts, score, keep_base, dgrid, dscore, n=20,
                              r_cover=200, d_min=150, curve_n=2000, pool=2000)
            
            n_public = (sel["PNU"].isin(nat_pnu if "국유지만" in sc["name"] else nat_pnu | city_pnu)).sum()
            scores = sel.head(20)["점수"].to_numpy()
            
            results.append({
                "가산점": f"+{b:.1f}",
                "Top20_내_해당_공유지_수": f"{n_public}개",
                "최소점수": f"{scores.min():.4f}",
                "최대점수": f"{scores.max():.4f}"
            })
            
        print(pd.DataFrame(results).to_markdown(index=False))

if __name__ == "__main__":
    run_split_experiment()
