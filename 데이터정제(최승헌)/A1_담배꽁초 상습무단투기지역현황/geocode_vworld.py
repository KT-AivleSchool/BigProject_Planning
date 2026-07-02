# -*- coding: utf-8 -*-
"""
브이월드(VWorld) 지오코딩 스크립트
용산구 담배꽁초 상습 무단투기 지역 현황 CSV → 위경도(EPSG:4326) 부여

전략:
  1) 도로명주소를 type=road 로 먼저 지오코딩
  2) 실패하거나 도로명주소가 비어있으면 지번주소를 type=parcel 로 폴백
  3) 결과에 위도/경도/출처/매칭주소/상태 컬럼 추가하여 저장

사용법:
  1) pip install requests pandas
  2) 아래 API_KEY 에 본인 브이월드 인증키 입력
  3) python geocode_vworld.py
"""

import time
import pandas as pd
import requests

# ─────────────────────────────────────────────
# 설정
# ─────────────────────────────────────────────
API_KEY = ""     # ← 본인 키로 교체
ENDPOINT = "https://api.vworld.kr/req/address"

INPUT_FILES = [
    "서울특별시_용산구_담배꽁초상습무단투기지역현황_20250806.csv",
    "서울특별시_용산구_담배꽁초상습무단투기지역현황_20240724.csv",
]
INPUT_ENCODING = "euc-kr"        # data.go.kr 원본 인코딩
OUTPUT_ENCODING = "utf-8-sig"    # 엑셀에서 한글 안 깨지게
SLEEP_SEC = 0.3                  # 호출 간 간격(과호출 방지)


# ─────────────────────────────────────────────
# 주소 정규화: "서울 " → "서울특별시 " 등
# ─────────────────────────────────────────────
def normalize(addr):
    if not isinstance(addr, str):
        return ""
    a = addr.strip()
    if a.startswith("서울 "):
        a = "서울특별시 " + a[len("서울 "):]
    return a


# ─────────────────────────────────────────────
# 브이월드 지오코더 호출 (단일 주소)
# addr_type: "road"(도로명) 또는 "parcel"(지번)
# 반환: (위도, 경도, 매칭주소) 또는 None
# ─────────────────────────────────────────────
def geocode(address, addr_type):
    address = normalize(address)
    if not address:
        return None
    params = {
        "service": "address",
        "request": "getcoord",
        "version": "2.0",
        "crs": "epsg:4326",
        "address": address,
        "refine": "true",
        "simple": "false",
        "format": "json",
        "type": addr_type,       # road | parcel
        "key": API_KEY,
    }
    try:
        r = requests.get(ENDPOINT, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  [요청오류] {address} ({addr_type}): {e}")
        return None

    resp = data.get("response", {})
    status = resp.get("status")
    if status != "OK":
        # NOT_FOUND / ERROR 등
        return None
    try:
        pt = resp["result"]["point"]
        lng = float(pt["x"])   # x = 경도(longitude)
        lat = float(pt["y"])   # y = 위도(latitude)
        matched = resp.get("refined", {}).get("text", address)
        return (lat, lng, matched)
    except (KeyError, ValueError, TypeError):
        return None


# ─────────────────────────────────────────────
# 한 행 처리: 도로명(road) → 실패시 지번(parcel) 폴백
# ─────────────────────────────────────────────
def geocode_row(road_addr, jibun_addr):
    # 1순위: 도로명주소
    res = geocode(road_addr, "road")
    if res:
        lat, lng, matched = res
        return lat, lng, "road", matched, "OK"
    # 2순위: 지번주소
    res = geocode(jibun_addr, "parcel")
    if res:
        lat, lng, matched = res
        return lat, lng, "parcel", matched, "OK(폴백)"
    # 둘 다 실패
    return None, None, None, None, "FAIL"


# ─────────────────────────────────────────────
# 파일 처리
# ─────────────────────────────────────────────
def process(path):
    df = pd.read_csv(path, encoding=INPUT_ENCODING)
    lats, lngs, srcs, matches, sts = [], [], [], [], []
    for _, row in df.iterrows():
        road = row.get("도로명주소", "")
        jibun = row.get("지번주소", "")
        lat, lng, src, matched, st = geocode_row(road, jibun)
        lats.append(lat); lngs.append(lng); srcs.append(src)
        matches.append(matched); sts.append(st)
        print(f"  #{row.get('연번')} [{st:8}] {matched}  ({lat}, {lng})")
        time.sleep(SLEEP_SEC)
    df["위도"] = lats
    df["경도"] = lngs
    df["지오코딩출처"] = srcs
    df["매칭주소"] = matches
    df["지오코딩상태"] = sts
    out = path.replace(".csv", "_geocoded.csv")
    df.to_csv(out, index=False, encoding=OUTPUT_ENCODING)
    ok = sum(1 for s in sts if s.startswith("OK"))
    print(f"  → 저장: {out}  (성공 {ok}/{len(df)})\n")
    return df


if __name__ == "__main__":
    if API_KEY.startswith("여기에"):
        raise SystemExit("먼저 API_KEY 에 브이월드 인증키를 입력하세요.")
    for f in INPUT_FILES:
        print("="*55, f"\n{f}")
        process(f)
    print("완료.")
