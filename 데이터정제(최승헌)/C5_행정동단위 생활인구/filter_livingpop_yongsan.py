# -*- coding: utf-8 -*-
"""
행정동단위 생활인구(LOCAL_PEOPLE_DONG) -> 용산구만 필터
용산구 자치구코드 11170으로 시작하는 행정동코드(8자리)를 추출한다.

데이터 주의: 이 CSV도 헤더보다 행에 빈 컬럼이 하나 더 붙어있어
             -> names에 _drop 추가 후 제거해야 컬럼이 안 밀림
결과: 생활인구_용산구_202605.csv (16개 행정동 × 24시간 × 31일)
"""

import pandas as pd

INPUT_FILE = "LOCAL_PEOPLE_DONG_202605.csv"
INPUT_ENCODING = "utf-8"          # 안 되면 "cp949"
OUTPUT_FILE = "생활인구_용산구_202605.csv"
OUTPUT_ENCODING = "utf-8-sig"
GU_CODE = "11170"                 # 용산구 자치구 코드(행정동코드 앞 5자리)


def main():
    # 끝 빈 컬럼 처리: 원본 헤더 + _drop
    hdr = pd.read_csv(INPUT_FILE, encoding=INPUT_ENCODING, nrows=0).columns.tolist()
    df = pd.read_csv(INPUT_FILE, encoding=INPUT_ENCODING, dtype=str,
                     header=0, names=hdr + ["_drop"], index_col=False)
    df = df.drop(columns=["_drop"])
    print(f"서울 전체 행: {len(df):,}")

    # 용산구 필터 (행정동코드 앞 5자리 == 11170)
    sub = df[df["행정동코드"].str.startswith(GU_CODE)].copy()
    dongs = sorted(sub["행정동코드"].unique())
    print(f"용산 행정동 {len(dongs)}개: {dongs}")
    print(f"용산 행 수: {len(sub):,}")

    # 인구 수치 컬럼 정수/실수화(총생활인구수 + 성·연령 컬럼)
    num_cols = [c for c in sub.columns if "생활인구수" in c]
    for c in num_cols:
        sub[c] = pd.to_numeric(sub[c], errors="coerce")

    sub.to_csv(OUTPUT_FILE, index=False, encoding=OUTPUT_ENCODING)
    print(f"저장 완료 -> {OUTPUT_FILE}")

    # 검증: 동별 평균 총생활인구(감 잡기용)
    print("\n[행정동별 평균 총생활인구]")
    g = sub.groupby("행정동코드")["총생활인구수"].mean().round(0).sort_values(ascending=False)
    print(g.to_string())


if __name__ == "__main__":
    main()
