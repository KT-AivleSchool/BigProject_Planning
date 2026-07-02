# -*- coding: utf-8 -*-
"""
소상공인 상가(상권)정보 서울 → 용산구만 추출
원본은 그대로 두고, 용산구 행만 별도 CSV로 저장한다.
"""

import pandas as pd

# ── 설정 ───────────────────────────────────────
INPUT_FILE = "소상공인시장진흥공단_상가(상권)정보_서울_202603.csv"
INPUT_ENCODING = "utf-8"          # 안 되면 "utf-8-sig"
TARGET = "용산구"
OUTPUT_FILE = "상가정보_용산구_202603.csv"
OUTPUT_ENCODING = "utf-8-sig"     # 엑셀에서 한글 안 깨짐

# 용량이 크면 저메모리 모드로 읽기 (서울 전체 수십만 행 대비)
df = pd.read_csv(INPUT_FILE, encoding=INPUT_ENCODING, dtype=str, low_memory=False)
print(f"원본 전체 행수: {len(df):,}")

# ── 용산구 필터 ────────────────────────────────
# 시군구명이 정확히 '용산구'인 행 (앞뒤 공백 방어)
mask = df["시군구명"].astype(str).str.strip() == TARGET
sub = df[mask].copy()
print(f"용산구 행수: {len(sub):,}")

# 좌표 결측 점검(선택)
missing_xy = sub["경도"].isna().sum() + sub["위도"].isna().sum()
if missing_xy:
    print(f"⚠️ 좌표 결측 셀 수: {missing_xy}")

# ── 저장 ───────────────────────────────────────
sub.to_csv(OUTPUT_FILE, index=False, encoding=OUTPUT_ENCODING)
print(f"저장 완료 → {OUTPUT_FILE}")

# 업종 대분류 분포 미리보기 (배후상권 감 잡기용)
print("\n[업종 대분류 분포]")
print(sub["상권업종대분류명"].value_counts().to_string())
