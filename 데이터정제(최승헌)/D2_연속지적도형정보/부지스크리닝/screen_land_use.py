# -*- coding: utf-8 -*-
"""
D-2 부지 스크리닝: 추천 입지 좌표 -> 필지 지목 판정 -> 3단계 등급
연속지적도(연속지적도형정보, EPSG:5186)에 좌표를 공간조인하여
각 후보의 지목과 점용 가능성 등급(점용후보/조건부/보류)을 붙인다.

⚠️ 소유구분(국유/공유/사유)은 이 데이터에 없음 -> '확정'이 아니라 '스크리닝'.
    최종 점용 가부는 브이월드 토지특성/국공유재산으로 별도 확인.
"""

import re
import pandas as pd
import geopandas as gpd

# ── 설정 ───────────────────────────────────────
LAND_SHP   = "AL_D002_11_20260608.shp"     # 연속지적도(세트파일 같은 폴더에)
LAND_ENC   = "cp949"                        # .cpg가 cp949
COORD_CSV  = "추천입지_후보.csv"            # 입력: 후보지명,경도,위도
COORD_ENC  = "utf-8-sig"
NAME_COL   = "후보지명"
LNG_COL    = "경도"
LAT_COL    = "위도"
A5_COL     = "A5"                           # 지번+지목 (끝글자=지목부호)
OUTPUT_CSV = "좌표별_부지판정.csv"
NEAREST_MAX_M = 20                          # within 실패 시 최근접 보정 허용거리(m). 조정 가능

# ── 지목부호 → 지목명 ──────────────────────────
JIMOK = {
    "전":"전","답":"답","과":"과수원","목":"목장용지","임":"임야","광":"광천지","염":"염전",
    "대":"대","장":"공장용지","학":"학교용지","차":"주차장","주":"주유소용지","창":"창고용지",
    "도":"도로","철":"철도용지","제":"제방","천":"하천","구":"구거","유":"유지","양":"양어장",
    "수":"수도용지","공":"공원","체":"체육용지","원":"유원지","종":"종교용지","사":"사적지",
    "묘":"묘지","잡":"잡종지",
}
# ── 3단계 등급 (명세서 §3, 조정 가능) ──────────
GRADE_점용후보 = {"도", "공", "차"}                                  # 도로·공원·주차장
GRADE_조건부   = {"천", "구", "유", "제", "체", "원", "철", "수", "잡"}  # 공공 가능/애매
# 나머지 지목부호는 모두 '보류'


def parse_jimok(a5):
    """A5(예: '179-3대', '산39-25임')의 끝글자로 지목부호 추출"""
    if not isinstance(a5, str) or not a5:
        return None, None
    ch = a5.strip()[-1]
    return (ch, JIMOK.get(ch)) if ch in JIMOK else (ch, None)


def grade(bu):
    if bu in GRADE_점용후보: return "점용후보"
    if bu in GRADE_조건부:   return "조건부"
    return "보류"


def main():
    # 1) 연속지적도 로드
    land = gpd.read_file(LAND_SHP, encoding=LAND_ENC)
    print(f"필지 수: {len(land):,} | 좌표계: {land.crs}")

    # 2) 추천 좌표 로드 -> Point(4326) -> 지적도 좌표계로 변환
    df = pd.read_csv(COORD_CSV, encoding=COORD_ENC)
    pts = gpd.GeoDataFrame(
        df.copy(),
        geometry=gpd.points_from_xy(df[LNG_COL], df[LAT_COL]),
        crs="EPSG:4326",
    ).to_crs(land.crs)

    # 3) 1차: within 공간조인
    land_cols = ["A1", "A3", "A4", A5_COL, "geometry"]
    j = gpd.sjoin(pts, land[land_cols], how="left", predicate="within")
    j["매칭방식"] = j["index_right"].notna().map({True: "within", False: None})

    # 4) within 실패분 -> 최근접 필지 보정(거리 임계 이내만)
    miss = j["index_right"].isna()
    if miss.any():
        near = gpd.sjoin_nearest(
            pts[miss.values], land[land_cols],
            how="left", max_distance=NEAREST_MAX_M, distance_col="_dist",
        )
        for col in ["A1", "A3", "A4", A5_COL]:
            j.loc[miss.values, col] = near[col].values
        j.loc[miss.values, "매칭방식"] = pd.Series(
            near["A1"].notna().map({True: "nearest", False: "미매칭"}).values,
            index=j.index[miss.values],
        )

    # 5) 지목 판별 + 등급
    parsed = j[A5_COL].map(parse_jimok)
    j["지목부호"] = parsed.map(lambda t: t[0])
    j["지목"]     = parsed.map(lambda t: t[1])
    j["판정등급"] = j["지목부호"].map(lambda b: grade(b) if pd.notna(b) else "미매칭")
    j.loc[j["매칭방식"] == "미매칭", "판정등급"] = "미매칭"

    # 6) 저장
    out = j[[NAME_COL, LNG_COL, LAT_COL, "A1", "A3", "A4", "지목", "판정등급", "매칭방식"]]
    out = out.rename(columns={"A1": "PNU", "A3": "법정동명", "A4": "지번"})
    out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"저장 -> {OUTPUT_CSV}")
    print("\n[등급 분포]"); print(out["판정등급"].value_counts().to_string())
    print("[매칭방식]"); print(out["매칭방식"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()
