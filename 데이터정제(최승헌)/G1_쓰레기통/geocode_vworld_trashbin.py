# -*- coding: utf-8 -*-
"""
브이월드(VWorld) 지오코딩 스크립트
용산구 가로휴지통 CSV의 '설치주소'를 위도/경도(EPSG:4326)로 변환합니다.

처리 전략
  1) 설치주소를 지번주소(type=parcel)로 먼저 조회
  2) 실패하면 도로명주소(type=road)로 재조회
  3) 위도, 경도, 지오코딩출처, 매칭주소, 지오코딩상태 컬럼 추가
  4) 같은 주소는 캐시하여 중복 API 호출 방지

사용법
  1) pip install pandas requests
  2) 아래 API_KEY에 본인의 브이월드 인증키 입력
  3) 이 파이썬 파일과 CSV 파일을 같은 폴더에 배치
  4) python geocode_vworld_가로휴지통.py
"""

import time
from pathlib import Path

import pandas as pd
import requests


# ─────────────────────────────────────────────
# 설정
# ─────────────────────────────────────────────
API_KEY = "8BDCECB2-2E9D-3154-9B3A-AA402E1545E0"  # 본인의 브이월드 인증키 입력

ENDPOINT = "https://api.vworld.kr/req/address"

INPUT_FILE = "서울특별시 용산구_가로휴지통_20240630.csv"
ADDRESS_COLUMN = "설치주소"

INPUT_ENCODINGS = ("cp949", "euc-kr", "utf-8-sig", "utf-8")
OUTPUT_ENCODING = "utf-8-sig"

SLEEP_SEC = 0.3
REQUEST_TIMEOUT = 10
MAX_RETRIES = 2


# ─────────────────────────────────────────────
# CSV 읽기
# ─────────────────────────────────────────────
def read_csv_auto(path):
    """후보 인코딩을 순서대로 시도하여 CSV를 읽습니다."""
    last_error = None

    for encoding in INPUT_ENCODINGS:
        try:
            df = pd.read_csv(path, encoding=encoding)
            print(f"[입력 인코딩] {encoding}")
            return df
        except UnicodeDecodeError as error:
            last_error = error

    raise UnicodeError(
        f"CSV 인코딩을 확인할 수 없습니다: {path}\n마지막 오류: {last_error}"
    )


# ─────────────────────────────────────────────
# 주소 정규화
# ─────────────────────────────────────────────
def normalize_address(address):
    """공백과 일부 행정구역 표기를 정리합니다."""
    if pd.isna(address):
        return ""

    normalized = " ".join(str(address).strip().split())

    if normalized.startswith("서울 "):
        normalized = "서울특별시 " + normalized[len("서울 "):]

    return normalized


# ─────────────────────────────────────────────
# 브이월드 API 단일 호출
# ─────────────────────────────────────────────
def geocode_once(address, address_type):
    """
    address_type:
      - parcel: 지번주소
      - road: 도로명주소

    성공 시 (위도, 경도, 매칭주소)를 반환하고,
    실패 시 None을 반환합니다.
    """
    normalized = normalize_address(address)

    if not normalized:
        return None

    params = {
        "service": "address",
        "request": "getcoord",
        "version": "2.0",
        "crs": "epsg:4326",
        "address": normalized,
        "refine": "true",
        "simple": "false",
        "format": "json",
        "type": address_type,
        "key": API_KEY,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                ENDPOINT,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            break

        except (requests.RequestException, ValueError) as error:
            print(
                f"  [요청 오류 {attempt}/{MAX_RETRIES}] "
                f"{normalized} ({address_type}): {error}"
            )

            if attempt == MAX_RETRIES:
                return None

            time.sleep(1)

    api_response = data.get("response", {})

    if api_response.get("status") != "OK":
        return None

    try:
        point = api_response["result"]["point"]

        longitude = float(point["x"])
        latitude = float(point["y"])

        matched_address = (
            api_response.get("refined", {}).get("text")
            or normalized
        )

        return latitude, longitude, matched_address

    except (KeyError, TypeError, ValueError):
        return None


# ─────────────────────────────────────────────
# 가로휴지통 주소 처리
# ─────────────────────────────────────────────
def geocode_trash_bin(address):
    """
    가로휴지통 CSV의 설치주소는 지번주소가 중심이므로
    parcel 조회 후 road 조회를 수행합니다.
    """
    parcel_result = geocode_once(address, "parcel")

    if parcel_result:
        latitude, longitude, matched_address = parcel_result
        return (
            latitude,
            longitude,
            "parcel",
            matched_address,
            "OK",
        )

    road_result = geocode_once(address, "road")

    if road_result:
        latitude, longitude, matched_address = road_result
        return (
            latitude,
            longitude,
            "road",
            matched_address,
            "OK(road 폴백)",
        )

    return None, None, None, None, "FAIL"


# ─────────────────────────────────────────────
# 전체 파일 처리
# ─────────────────────────────────────────────
def process(input_file):
    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(
            f"입력 파일을 찾을 수 없습니다: {input_path.resolve()}"
        )

    df = read_csv_auto(input_path)

    if ADDRESS_COLUMN not in df.columns:
        raise KeyError(
            f"'{ADDRESS_COLUMN}' 컬럼이 없습니다.\n"
            f"현재 컬럼: {list(df.columns)}"
        )

    latitudes = []
    longitudes = []
    sources = []
    matched_addresses = []
    statuses = []

    # 동일 주소 중복 호출 방지
    cache = {}

    total_count = len(df)

    for row_index, row in df.iterrows():
        management_number = row.get("관리번호", row_index + 1)
        address = normalize_address(row.get(ADDRESS_COLUMN, ""))

        if not address:
            result = (None, None, None, None, "EMPTY_ADDRESS")

        elif address in cache:
            result = cache[address]

        else:
            result = geocode_trash_bin(address)
            cache[address] = result
            time.sleep(SLEEP_SEC)

        latitude, longitude, source, matched, status = result

        latitudes.append(latitude)
        longitudes.append(longitude)
        sources.append(source)
        matched_addresses.append(matched)
        statuses.append(status)

        print(
            f"[{row_index + 1:03}/{total_count}] "
            f"관리번호={management_number} "
            f"[{status}] {address} "
            f"-> ({latitude}, {longitude})"
        )

    df["위도"] = latitudes
    df["경도"] = longitudes
    df["지오코딩출처"] = sources
    df["매칭주소"] = matched_addresses
    df["지오코딩상태"] = statuses

    output_path = input_path.with_name(
        f"{input_path.stem}_geocoded.csv"
    )

    df.to_csv(
        output_path,
        index=False,
        encoding=OUTPUT_ENCODING,
    )

    success_count = sum(
        1 for status in statuses
        if str(status).startswith("OK")
    )
    fail_count = sum(
        1 for status in statuses
        if status == "FAIL"
    )
    empty_count = sum(
        1 for status in statuses
        if status == "EMPTY_ADDRESS"
    )

    print("\n" + "=" * 60)
    print(f"전체 행: {total_count}")
    print(f"고유 주소: {len(cache)}")
    print(f"성공: {success_count}")
    print(f"실패: {fail_count}")
    print(f"빈 주소: {empty_count}")
    print(f"저장 파일: {output_path.resolve()}")
    print("=" * 60)

    return df


if __name__ == "__main__":
    if not API_KEY.strip():
        raise SystemExit(
            "API_KEY가 비어 있습니다. "
            "브이월드 인증키를 입력한 뒤 다시 실행하세요."
        )

    process(INPUT_FILE)
