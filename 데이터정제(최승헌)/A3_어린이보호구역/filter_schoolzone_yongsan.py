# -*- coding: utf-8 -*-
"""
전국 어린이보호구역 표준데이터 → 용산구만 추출
이 데이터는 '시군구명' 컬럼이 없어 주소로 필터한다.
('용산구'는 서울에만 있는 자치구라 주소 포함 매칭이 안전)
원본은 그대로 두고 용산구 행만 별도 CSV로 저장.
"""

import pandas as pd

# ── 설정 ───────────────────────────────────────
INPUT_FILE = "전국어린이보호구역표준데이터.csv"
INPUT_ENCODING = "cp949"          # 원본 인코딩(표준데이터는 cp949)
TARGET = "용산구"
OUTPUT_FILE = "어린이보호구역_용산구.csv"
OUTPUT_ENCODING = "utf-8-sig"     # 엑셀에서 한글 안 깨짐

# ── 로드 ───────────────────────────────────────
df = pd.read_csv(INPUT_FILE, encoding=INPUT_ENCODING, dtype=str, low_memory=False)
print(f"전국 전체 행: {len(df):,}")

# ── 용산구 필터 (도로명 OR 지번 주소에 '용산구' 포함) ──
road = df["소재지도로명주소"].fillna("")
jibun = df["소재지지번주소"].fillna("")
mask = road.str.contains(TARGET) | jibun.str.contains(TARGET)
sub = df[mask].copy()
print(f"용산구 행: {len(sub)}")

# ── 검수 로그 ──────────────────────────────────
# 오탐 방지: 걸린 행의 제공기관명이 모두 용산구인지 확인
orgs = sub["제공기관명"].unique().tolist()
print("제공기관명:", orgs)
lat = sub["위도"].astype(float)
lng = sub["경도"].astype(float)
print(f"좌표 범위: 위도 {lat.min():.4f}~{lat.max():.4f} / 경도 {lng.min():.4f}~{lng.max():.4f}")
print("시설종류 분포:", dict(sub["시설종류"].value_counts()))

# ── 저장 ───────────────────────────────────────
sub.to_csv(OUTPUT_FILE, index=False, encoding=OUTPUT_ENCODING)
print(f"저장 완료 → {OUTPUT_FILE}")
