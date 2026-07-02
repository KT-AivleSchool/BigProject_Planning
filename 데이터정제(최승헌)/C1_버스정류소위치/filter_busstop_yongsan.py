# -*- coding: utf-8 -*-
"""
서울시 버스정류소 위치정보 → 용산구 정류소만 추출
정류소 데이터엔 '구' 컬럼이 없으므로 좌표로 필터한다.
  1) 용산구 대략 bbox로 후보를 좁힘(API 호출 최소화)
  2) 브이월드 역지오코딩으로 각 후보의 시군구를 확인 → '용산구'만 남김
결과: 용산 정류소 CSV + ARS 목록(승하차 데이터 필터용 화이트리스트)

정류소 위치는 월별로 거의 불변 → 최신 파일 하나만 돌리면 됨.
"""

import time
import pandas as pd
import requests

# ── 설정 ───────────────────────────────────────
API_KEY = ""     # ← A-1에서 쓴 키 그대로
INPUT_FILE = "서울시버스정류소위치정보(20260602).xlsx"   # 최신본
OUTPUT_ENCODING = "utf-8-sig"
SLEEP_SEC = 0.2
ENDPOINT = "https://api.vworld.kr/req/address"

# 용산구 대략 bbox (넉넉히 잡고, 실제 판정은 역지오코딩으로)
BBOX = dict(xmin=126.94, xmax=127.02, ymin=37.515, ymax=37.560)


# ── 역지오코딩: 좌표 → 시군구 ──────────────────
def get_sigungu(x, y):
    params = {
        "service": "address", "request": "getAddress", "version": "2.0",
        "crs": "epsg:4326", "point": f"{x},{y}", "format": "json",
        "type": "parcel", "key": API_KEY,
    }
    try:
        r = requests.get(ENDPOINT, params=params, timeout=10)
        data = r.json()
    except Exception:
        return None
    resp = data.get("response", {})
    if resp.get("status") != "OK":
        return None
    try:
        st = resp["result"][0]["structure"]
        return st.get("level2")   # level1=시도, level2=시군구
    except (KeyError, IndexError, TypeError):
        return None


# ── 메인 ───────────────────────────────────────
def main():
    df = pd.read_excel(INPUT_FILE, dtype=str)
    df["x"] = pd.to_numeric(df["X좌표"], errors="coerce")
    df["y"] = pd.to_numeric(df["Y좌표"], errors="coerce")

    cand = df[(df.x.between(BBOX["xmin"], BBOX["xmax"])) &
              (df.y.between(BBOX["ymin"], BBOX["ymax"]))].copy()
    print(f"전체 {len(df):,} → bbox 후보 {len(cand)} (역지오코딩 대상)")

    sigungu, fail = [], 0
    for i, (_, row) in enumerate(cand.iterrows(), 1):
        g = get_sigungu(row["x"], row["y"])
        sigungu.append(g)
        if g is None:
            fail += 1
        if i % 100 == 0:
            print(f"  ...{i}/{len(cand)} 처리")
        time.sleep(SLEEP_SEC)
    cand["시군구"] = sigungu

    yongsan = cand[cand["시군구"] == "용산구"].copy()
    print(f"→ 용산구 정류소: {len(yongsan)}건 (역지오코딩 실패 {fail}건)")

    # 결과 저장 (원본 컬럼만 유지)
    keep = ["NODE_ID", "ARS_ID", "정류소명", "X좌표", "Y좌표", "정류소타입"]
    yongsan[keep].to_csv("버스정류소_용산구.csv", index=False, encoding=OUTPUT_ENCODING)
    print("저장 → 버스정류소_용산구.csv")

    # ARS 화이트리스트(승하차 데이터 필터용)
    yongsan[["ARS_ID"]].drop_duplicates().to_csv(
        "버스정류소_용산구_ARS목록.csv", index=False, encoding=OUTPUT_ENCODING)
    print("저장 → 버스정류소_용산구_ARS목록.csv  (C-3 승하차 필터에 사용)")


if __name__ == "__main__":
    if API_KEY.startswith("여기에"):
        raise SystemExit("먼저 API_KEY에 브이월드 인증키를 입력하세요.")
    main()
