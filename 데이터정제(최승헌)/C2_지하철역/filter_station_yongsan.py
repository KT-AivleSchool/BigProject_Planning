# -*- coding: utf-8 -*-
"""
서울시 역사마스터(원본 784행) → 용산구 역 추출
좌표를 브이월드 역지오코딩하여 자치구=='용산구'인 역만 남긴다.
경계 역(서울역 등)은 좌표 판정 그대로 따른다.
결과: 역사마스터_용산구.csv
"""

import time
import pandas as pd
import requests

API_KEY = ""     # ← A-1 키 그대로
INPUT_FILE = "서울시 역사마스터 정보.csv"
INPUT_ENCODING = "cp949"
OUTPUT_ENCODING = "utf-8-sig"
SLEEP_SEC = 0.2
ENDPOINT = "https://api.vworld.kr/req/address"
BBOX = dict(xmin=126.94, xmax=127.02, ymin=37.515, ymax=37.560)  # API 호출 최소화용


def get_sigungu(x, y):
    params = {"service": "address", "request": "getAddress", "version": "2.0",
              "crs": "epsg:4326", "point": f"{x},{y}", "format": "json",
              "type": "parcel", "key": API_KEY}
    try:
        resp = requests.get(ENDPOINT, params=params, timeout=10).json()["response"]
    except Exception:
        return None
    if resp.get("status") != "OK":
        return None
    try:
        return resp["result"][0]["structure"].get("level2")  # 시군구
    except (KeyError, IndexError, TypeError):
        return None


def main():
    df = pd.read_csv(INPUT_FILE, encoding=INPUT_ENCODING, dtype=str)
    df["y"] = pd.to_numeric(df["위도"], errors="coerce")
    df["x"] = pd.to_numeric(df["경도"], errors="coerce")

    # 1차 bbox로 후보만 추림(전국 784개 전량 호출 방지)
    cand = df[(df.x.between(BBOX["xmin"], BBOX["xmax"])) &
              (df.y.between(BBOX["ymin"], BBOX["ymax"]))].copy()
    print(f"전체 {len(df)} -> bbox 후보 {len(cand)} 역지오코딩")

    gu, fail = [], 0
    for _, r in cand.iterrows():
        g = get_sigungu(r["x"], r["y"])
        gu.append(g)
        if g is None:
            fail += 1
        time.sleep(SLEEP_SEC)
    cand["자치구"] = gu

    yongsan = cand[cand["자치구"] == "용산구"].copy()
    keep = ["역사_ID", "역사명", "호선", "위도", "경도", "자치구"]
    yongsan[keep].to_csv("역사마스터_용산구.csv", index=False, encoding=OUTPUT_ENCODING)
    print(f"-> 용산구 역: {len(yongsan)}건 (역지오코딩 실패 {fail}건) -> 역사마스터_용산구.csv")
    print("\n[추출된 용산 역]")
    print(yongsan[["역사명", "호선", "자치구"]].to_string(index=False))


if __name__ == "__main__":
    if API_KEY.startswith("여기에"):
        raise SystemExit("먼저 API_KEY에 브이월드 인증키를 입력하세요.")
    main()
