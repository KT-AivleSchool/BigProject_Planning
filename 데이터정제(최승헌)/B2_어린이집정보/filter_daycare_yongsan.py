# -*- coding: utf-8 -*-
"""
서울시 어린이집 표준데이터 → 용산구 추출
규제 배제 버퍼(30~50m)용이므로 '폐지' 시설을 걸러낸 운영중 파일을 별도로 생성.
원본은 그대로 두고 두 개의 결과 CSV를 만든다.
  ① 어린이집_용산구_전체.csv    (참고용, 폐지 포함)
  ② 어린이집_용산구_운영중.csv  (규제 버퍼용, 정상+재개만)
"""

import pandas as pd

# ── 설정 ───────────────────────────────────────
INPUT_FILE = "서울시 어린이집 정보(표준 데이터).csv"
INPUT_ENCODING = "cp949"
OUTPUT_ENCODING = "utf-8-sig"
TARGET = "용산구"
LAT_COL = "시설 위도(좌표값)"
LNG_COL = "시설 경도(좌표값)"
ACTIVE_STATUS = ["정상", "재개"]   # 운영중으로 볼 상태

# ── 로드 & 용산 필터 ───────────────────────────
df = pd.read_csv(INPUT_FILE, encoding=INPUT_ENCODING, dtype=str, low_memory=False)
print(f"서울 전체 행: {len(df):,}")

sub = df[df["시군구명"].astype(str).str.strip() == TARGET].copy()
print(f"용산구 전체: {len(sub)}")
print("운영현황 분포:", dict(sub["운영현황"].value_counts(dropna=False)))

# ── 좌표 결측 점검 ─────────────────────────────
lat = pd.to_numeric(sub[LAT_COL], errors="coerce")
miss = lat.isna().sum()
if miss:
    print(f"⚠️ 좌표 결측 {miss}건 (버퍼 연산 시 제외되거나 상세주소 지오코딩 필요)")

# ── ① 전체 저장 ────────────────────────────────
sub.to_csv("어린이집_용산구_전체.csv", index=False, encoding=OUTPUT_ENCODING)
print("저장 → 어린이집_용산구_전체.csv")

# ── ② 운영중만 저장 (규제 버퍼용) ──────────────
active = sub[sub["운영현황"].isin(ACTIVE_STATUS)].copy()
active.to_csv("어린이집_용산구_운영중.csv", index=False, encoding=OUTPUT_ENCODING)
print(f"저장 → 어린이집_용산구_운영중.csv  (운영중 {len(active)}건)")

print("\n※ 라이선스 제4유형(상업이용금지) — 상업 배포물에는 좌표 직접노출 주의, "
      "규제 버퍼 연산 후 결과만 사용 권장. 대체: 어린이보호구역(A-3, 제한없음).")
