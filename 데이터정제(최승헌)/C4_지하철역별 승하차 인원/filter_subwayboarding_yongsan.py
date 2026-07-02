# -*- coding: utf-8 -*-
"""
지하철 역별 승하차(CARD_SUBWAY_MONTH) -> 용산구 역만 필터
C-2에서 만든 용산 역사마스터(C2_역사마스터_용산구.csv)의 역명으로 거른다.

조인: 역명만 사용(호선 무시) + 양쪽 괄호'(...)' 제거 후 매칭  -> A안
데이터 주의: 이 CSV는 헤더 6개인데 행마다 끝에 빈 컬럼이 하나 더 붙음
             -> names 7개로 읽어 마지막 _drop 컬럼 제거
결과: 지하철승하차_용산구_202605.csv (+ 매칭 검증 로그)
"""

import re
import pandas as pd

# ── 설정 ───────────────────────────────────────
BOARDING_FILE = "CARD_SUBWAY_MONTH_202605.csv"
BOARDING_ENCODING = "utf-8"          # 안 되면 "cp949"
STATION_FILE = "C2_역사마스터_용산구.csv"
STATION_ENCODING = "utf-8-sig"       # 안 되면 "utf-8"
OUTPUT_FILE = "지하철승하차_용산구_202605.csv"
OUTPUT_ENCODING = "utf-8-sig"


def strip_paren(s):
    """역명 정규화: 괄호와 그 안 내용 제거 + 공백 제거"""
    return re.sub(r"\(.*?\)", "", str(s)).strip()


def main():
    # 1) 용산 역명 집합(괄호 제거)
    st = pd.read_csv(STATION_FILE, encoding=STATION_ENCODING, dtype=str)
    yongsan_names = set(strip_paren(n) for n in st["역사명"].dropna())
    print(f"용산 역명(괄호제거) {len(yongsan_names)}개: {sorted(yongsan_names)}")

    # 2) 승하차 로드 (끝 빈 컬럼 처리: names 7개)
    cols = ["사용일자", "노선명", "역명", "승차총승객수", "하차총승객수", "등록일자", "_drop"]
    df = pd.read_csv(BOARDING_FILE, encoding=BOARDING_ENCODING, dtype=str,
                     header=0, names=cols, index_col=False)
    df = df.drop(columns=["_drop"])
    print(f"승하차 전체 행: {len(df):,}")

    # 3) 역명 정규화 후 필터
    df["_name"] = df["역명"].map(strip_paren)
    out = df[df["_name"].isin(yongsan_names)].drop(columns=["_name"]).copy()

    # 숫자 컬럼 정리(문자->정수, 콤마 방어)
    for c in ["승차총승객수", "하차총승객수"]:
        out[c] = pd.to_numeric(out[c].str.replace(",", "", regex=False), errors="coerce")

    out.to_csv(OUTPUT_FILE, index=False, encoding=OUTPUT_ENCODING)

    # 4) 검증 로그
    matched = set(out["역명"].map(strip_paren).unique())
    miss = yongsan_names - matched
    print("\n===== 검증 =====")
    print(f"용산 승하차 행: {len(out):,} -> {OUTPUT_FILE}")
    print(f"매칭된 역: {len(matched)}/{len(yongsan_names)}")
    if miss:
        print(f"  ⚠️ 승하차에 안 잡힌 역: {sorted(miss)}")
    print("\n[역별 월 합계 상위]")
    g = (out.groupby(out["역명"].map(strip_paren))[["승차총승객수", "하차총승객수"]]
           .sum().sort_values("승차총승객수", ascending=False))
    print(g.to_string())


if __name__ == "__main__":
    main()
