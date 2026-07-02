# -*- coding: utf-8 -*-
"""
버스 정류장별 승하차(월 148MB) -> 용산구 정류장만 필터
C-1에서 만든 ARS 화이트리스트(버스정류소_용산구_ARS목록.csv)로 거른다.

조인: 승하차 '버스정류장ARS번호'  ==  화이트리스트 'ARS_ID'
  - 승하차 ARS번호는 0이 빠져있음(예: 1157) -> 양쪽 다 5자리 zfill로 정규화
대용량이라 청크로 읽어 메모리 보호.
결과: 버스승하차_용산구_202605.csv (+ 매칭 검증 로그)
"""

import pandas as pd

# ── 설정 ───────────────────────────────────────
BOARDING_FILE = "BUS_STATION_BOARDING_MONTH_202605.csv"
BOARDING_ENCODING = "cp949"
WHITELIST_FILE = "버스정류소_용산구_ARS목록.csv"
WHITELIST_ENCODING = "utf-8-sig"     # 안 되면 "utf-8"
OUTPUT_FILE = "버스승하차_용산구_202605.csv"
OUTPUT_ENCODING = "utf-8-sig"
ARS_COL = "버스정류장ARS번호"        # 승하차 쪽 조인 키
CHUNK = 200_000


def norm(s):
    """ARS번호 정규화: 공백제거 + 5자리 zfill"""
    return s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(5)


def main():
    # 1) 화이트리스트 로드 & 정규화
    try:
        wl = pd.read_csv(WHITELIST_FILE, encoding=WHITELIST_ENCODING, dtype=str)
    except UnicodeDecodeError:
        wl = pd.read_csv(WHITELIST_FILE, encoding="utf-8", dtype=str)
    wl_ars = set(norm(wl["ARS_ID"]))
    print(f"화이트리스트 정류장: {len(wl_ars)}개")
    print("  샘플:", sorted(list(wl_ars))[:5])

    # 2) 승하차 청크 처리
    parts = []
    total_rows = 0
    matched_ars = set()
    for i, chunk in enumerate(pd.read_csv(
            BOARDING_FILE, encoding=BOARDING_ENCODING, dtype=str, chunksize=CHUNK), 1):
        total_rows += len(chunk)
        chunk["_ars5"] = norm(chunk[ARS_COL])
        hit = chunk[chunk["_ars5"].isin(wl_ars)].copy()
        if len(hit):
            matched_ars.update(hit["_ars5"].unique())
            parts.append(hit.drop(columns=["_ars5"]))
        print(f"  청크 {i}: 누적 {total_rows:,}행, 용산 매칭 {sum(len(p) for p in parts):,}행")

    if not parts:
        print("⚠️ 매칭된 행이 없음 -> ARS 형식/화이트리스트 확인 필요")
        return
    out = pd.concat(parts, ignore_index=True)
    out.to_csv(OUTPUT_FILE, index=False, encoding=OUTPUT_ENCODING)

    # 3) 검증 로그
    cover = len(matched_ars)
    print("\n===== 검증 =====")
    print(f"원본 전체 행: {total_rows:,}")
    print(f"용산 승하차 행: {len(out):,}  -> {OUTPUT_FILE}")
    print(f"화이트리스트 커버율: {cover}/{len(wl_ars)} 정류장 매칭")
    miss = wl_ars - matched_ars
    if miss:
        print(f"  승하차에 안 잡힌 정류장 {len(miss)}개(가상/폐지/무이용일 가능성):",
              sorted(list(miss))[:10])


if __name__ == "__main__":
    main()
