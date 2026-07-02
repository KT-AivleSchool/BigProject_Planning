# -*- coding: utf-8 -*-
"""
E-1 민원 빅데이터: 용산구 흡연 관련 민원 건수 조회 (배경 지표용)
API: 2024 [키워드 기반 민원발생지별 정보] minPttnStstAddrInfo
     -> 키워드로 검색된 민원을 '발생지 시군구' 단위로 집계
방침(확정): 넓은 검색어 / 전체 민원 / 최근 1년 / 전국 결과에서 용산구 필터

주의:
 - 개발계정 트래픽 100회/일. 이 스크립트는 1회 호출.
 - 결과에 용산구가 없으면(상위 목록 밖) mainSubCode(용산구청 코드) 폴백 필요.
   -> 용산구청 코드는 공개표에 없음. 국민신문고 헬프데스크(1600-8172) 문의.
"""

import requests

# ── 설정 ───────────────────────────────────────
API_KEY = ""   # 공공데이터포털 '일반 인증키(Decoding)' 권장
ENDPOINT = "http://apis.data.go.kr/1140100/minAnalsInfoView7/minPttnStstAddrInfo"

SEARCHWORD = "(간접흡연+OR+담배꽁초)"  # 넓게. +와 () 그대로 유지
TARGET = "pttn,dfpt,saeol"        # 일반+고충+수집 전체
DATE_FROM = "20250101"
DATE_TO = "20251231"
SEARCH_OPTION = "B0060005"        # 제목+내용
OMIT_DUPLICATE = "false"

MAIN_SUB_CODE = ""                # 폴백용 용산구청 코드(없으면 공백 = 전국 발생지별)
TARGET_GU = "용산구"


def call_api():
    params = {
        "serviceKey": API_KEY,
        "target": TARGET,
        "searchword": SEARCHWORD,
        "dateFrom": DATE_FROM,
        "dateTo": DATE_TO,
        "searchOption": SEARCH_OPTION,
        "omitDuplicate": OMIT_DUPLICATE,
        "dataType": "json",
    }
    if MAIN_SUB_CODE.strip():
        params["mainSubCode"] = MAIN_SUB_CODE.strip()

    # searchword의 '+'가 %2B로 바뀌면 서버가 OR로 인식 못 할 수 있어
    # -> 인코딩을 직접 통제하기 위해 params를 문자열로 구성(+, () 보존)
    from urllib.parse import quote
    q = (
        f"serviceKey={API_KEY}"
        f"&target={TARGET}"
        f"&searchword={quote(SEARCHWORD, safe='()+')}"
        f"&dateFrom={DATE_FROM}&dateTo={DATE_TO}"
        f"&searchOption={SEARCH_OPTION}&omitDuplicate={OMIT_DUPLICATE}&dataType=json"
    )
    if MAIN_SUB_CODE.strip():
        q += f"&mainSubCode={MAIN_SUB_CODE.strip()}"
    url = f"{ENDPOINT}?{q}"

    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()


def parse(data):
    # 응답 구조: body.items[].item.{label, hits}
    body = data.get("body", data.get("response", {}).get("body", {}))
    items = body.get("items", [])
    rows = []
    for it in items:
        node = it.get("item", it)
        rows.append((node.get("label"), node.get("hits")))
    return rows, body.get("totalCount")


def main():
    if API_KEY.startswith("여기에"):
        raise SystemExit("먼저 API_KEY에 인증키(Decoding)를 입력하세요.")
    data = call_api()
    rows, total = parse(data)
    print(f"발생지별 결과 {len(rows)}건 (totalCount={total})")
    print("상위 목록:")
    for label, hits in rows:
        print(f"  {label}: {hits}")

    # 용산구 필터
    ys = [(l, h) for l, h in rows if l and TARGET_GU in l]
    print("\n===== 용산구 =====")
    if ys:
        for l, h in ys:
            print(f"  {l}: {h}건")
    else:
        print(f"  ⚠️ 결과에 '{TARGET_GU}' 없음. 이 기능은 상위 N개만 반환하는 것으로 보임.")
        print("     대응: ① 검색어를 더 좁혀(예: (간접흡연+OR+담배꽁초)) 재호출")
        print("          ② 헬프데스크(1600-8172)로 용산구청 코드 받아 MAIN_SUB_CODE에 입력")


if __name__ == "__main__":
    main()
