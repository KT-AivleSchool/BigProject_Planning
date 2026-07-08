# 🛡️ Step 1~3 AI 감리 및 동적 가중치 피벗 구현 계획서 (Implementation Plan)

본 문서는 사용자의 기획 변경 및 피벗 요청에 따라 **"Step 1 CSV 감리 및 동적 가중치 추출"**, **"Step 2 의도(Intent) HITL 수정 및 좌표 보정 제거"**, **"Step 3 동적 가중치 슬라이더 연동"**을 백엔드(FastAPI) 및 프론트엔드(Next.js)에 설계 및 이식하기 위한 기술 구현 계획서입니다.

---

## 🛠️ User Review Required

> [!IMPORTANT]
> **핵심 아키텍처 규칙 및 피벗 요지**
> 1. **Step 1 파일 제한**: 드롭존 업로드 시 오직 **CSV 파일만** 허용합니다. (RAG 법규 데이터는 별도 관리 모달을 통해 **PDF 파일만** 취급합니다.)
> 2. **Step 1 LLM 감리 및 로컬 격리**: 업로드된 CSV 데이터를 기반으로 추출된 AI 감리 결과(audit_reason), 사용자의 정보 추출 의도(user_intent), 가중치 인자들(extracted_weights)은 **오직 프론트엔드 상태(Client React State)로만 보존**하며, 백엔드 DB나 서버 세션에 절대 전송하지 않아 프라이버시 및 격리를 만족합니다.
> 3. **Step 2 물리 좌표 보정 제거**: 기존 지도의 핀 드래그앤드롭 이벤트 리스너 및 위경도 숫자 인풋 폼은 **완전히 소거**합니다. 대신 Step 1에서 추출된 **"사용자의 추출 의도(user_intent)"를 직접 텍스트로 보정(HITL)**하는 편집 창을 제공합니다.
> 4. **Step 3 동적 가중치 슬라이더**: 고정된 5대 요인 대신, **Step 1에서 동적으로 추출된 가중치 인자 항목들**이 슬라이더 UI에 매핑되어 조절 가능하도록 구현합니다.

---

## 📂 Proposed Changes

### 1️⃣ 백엔드 (FastAPI) 개편
#### [MODIFY] [lands.py](file:///Users/jcm0314/Downloads/빅프로젝트/backend/app/api/v1/lands.py)
*   `POST /api/v1/lands/audit/csv` 신규 API 추가:
    *   오직 CSV 포맷만 수신 제한 (`filename.lower().endswith('.csv')` 검사 및 400 에러 처리).
    *   모의 LLM을 가동하여 감리 사유(`audit_reason`), 사용자 추출 의도(`user_intent`), 동적 가중치 항목(`extracted_weights`) 맵을 반환하도록 DTO 설계.

---

### 2️⃣ 프론트엔드 (Next.js) 개편
#### [MODIFY] [page.js](file:///Users/jcm0314/Downloads/빅프로젝트/frontend/src/app/page.js)
*   **상태 변수 개편**:
    *   `auditReason`, `userIntent`, `ahpWeights` 상태값을 동적으로 수용하도록 구조 변경.
    *   `ahpWeights`의 초기값을 빈 객체 `{}`로 변경하고, CSV 업로드 성공 시 API 결과값으로 갱신.
*   **Step 1 드롭존 파일 가드**:
    *   업로드 핸들러에서 파일 확장자가 `.csv`가 아닌 경우 업로드를 즉각 차단하고 경고 팝업 가동.
    *   CSV 파일 업로드 시 `POST /api/v1/lands/audit/csv`로 요청하여 결과 수신 후 React State에 바인딩.
*   **Step 2 좌표 보정 제거 및 의도(Intent) HITL 전환**:
    *   기존 지도의 `draggable: true` 마커 속성을 `draggable: false`로 비활성화하고, `drag`, `dragend` 등의 좌표 계산 경고 로직 일체 소거.
    *   우측 패널에 주황색 핀 좌표 보정 폼 대신, **"추출된 정보 탐색 의도"**를 수정할 수 있는 `textarea` 입력창 연동.
    *   보정 완료 클릭 시 백엔드 `/hitl/commit` 통신을 삭제하고, 오직 프론트엔드 상태값 `userIntent`만 동적으로 갱신한 뒤 Step 3로 천이.
*   **Step 3 동적 가중치 슬라이더 바인딩**:
    *   `Object.keys(ahpWeights).map(...)`을 사용하여 LLM이 추출한 가중치 키들을 기준으로 슬라이더 개수와 요인명을 가변 렌더링.
    *   AHP 락 버튼 클릭 시 `buildPairwiseMatrix` 함수가 이 동적 키들을 기반으로 크기 및 성분비를 연산하여 백엔드 `/ahp/calculate`에 전송하도록 수학적 로직 보정.

---

## 🧪 Verification Plan

### Automated Tests
*   `npm run lint` 및 `npm run build` 컴파일 빌드를 통과하는지 확인.
*   백엔드 API 테스트(FastAPI Swagger)를 기동하여 `POST /api/v1/lands/audit/csv` 동작 검리.

### Manual Verification
*   프론트엔드에 접속하여 non-csv 파일 업로드 차단 확인.
*   CSV 업로드 시 우측에 LLM 감리 사유 및 사용자 의도가 바인딩되는지 교차 확인.
*   Step 2에서 위경도 보정 폼이 사라지고 의도(user_intent) 텍스트 편집기 및 HITL 기능이 정상 가동되는지 확인.
*   Step 3 슬라이더가 동적 추출 키들로 유연하게 노출되는지 확인.
