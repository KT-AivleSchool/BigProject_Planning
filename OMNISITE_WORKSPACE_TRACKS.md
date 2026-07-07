# 🛡️ OmniSite 프로젝트 선행 가이드라인 기반 협업 명세 (ADR-003)

본 문서는 스마트시티 SDSS 플랫폼 **OmniSite**의 애자일 개발 생산성을 높이기 위해 채택한 **"조장 선행 R&D ➔ 개발팀 마스터 병합 및 고도화"** 협업 모델과 통합 형상관리 정책을 기록한 기술 명세입니다.

---

## 📄 기술 선도 협업 모델 (Leader-Driven Fast Track)
*   **협업 메커니즘**: 
    1.  **조례 RAG 독립 관리 및 Deletion Engine** 등의 신규/예외 레이어는 조장(배종현)이 단독 고도화 트랙에서 고속으로 선행 검증(PoC)합니다.
    2.  검증 완료된 기능(DTO 스펙, API 뼈대, Mock 가이드)은 즉시 **마스터 개발팀의 마스터 브랜치(`main`)에 공식 병합(Merge)**하여 동기화합니다.
    3.  PM(장천명)과 개발팀원(동현, 규민 등)은 이 이식된 뼈대 소스코드를 기점으로 **비동기 DB 세션 주입(`get_db`), PostGIS 공간 차집합 연산 및 실시간 SSE 스트리밍 라우팅**을 실물 구현 및 유기적 결합해 나갑니다.

---

## 🗺️ 1주차 스프린트 통합 피처 매핑 현황

```
[OmniSite 통합 마스터 브랜치 (main)]
       │
       ├─► ⚖️ [조장 배종현 님 선행 이식분]
       │    └─ RAG 조례 PDF 독립 다중 업로드 모달 분리 창구 탑재
       │    └─ 조례 목록 비동기 조회 및 Deletion 캐시 수거 물리 삭제 엔진 구축
       │    └─ 회원가입/JWT 로그인 이관에 따른 API 모킹 가이드 배포
       │
       └─► 🛠️ [PM 장천명 및 개발팀 고도화 연동분]
            └─ Next.js - FastAPI SSE 스트리밍 토론 채널 비동기 가동
            └─ Docker PostgreSQL/PostGIS 로컬 DB 기동 및 비동기 SQLAlchemy 2.0 세션 포팅
            └─ e2e_test.py 스크립트 기반 E2E 연동 테스트 자가검증 완료
```

### 1️⃣ 조장 선행 설계 이식 완료 내역
*   **조례 다중 업로드**: `POST /api/v1/upload/regulation` 및 프론트 UI 개편을 통해 RAG용 다중 PDF 법규 업로드 체계를 이식했습니다.
*   **조례 목록 비동기 조회**: 상단 네비게이션 헤더에 `📋 조례 목록 조회` 독립 모달 팝업을 배치해 `GET /api/v1/upload/regulations` API와 연동을 마쳤습니다.
*   **캐시 수거 물리 삭제 엔진**: `DELETE /api/v1/upload/regulations/{filename}` API로 원본 PDF와 임베딩용 텍스트 캐시(`[파일명].txt`) 물리 동시 소거 구조를 확보했습니다.

### 2️⃣ 마스터 개발팀 추가 고도화 완료 내역
*   **SSE 실시간 토론 중계**: FastAPI의 `EventSourceResponse` 기반 실시간 1.5초 간격 토론 대사 스트리밍 및 종결(`is_finished`) 검출 시 최종 통계 API(`/results`) 자동 Fetch 바인딩 구현.
*   **비동기 DB 팩토리 포팅**: `docker-compose.yml` 기반 로컬 Postgres(PostGIS+pgvector) 컨테이너 가동 성공 및 SQLAlchemy 2.0 비동기 헬퍼(`session.py` 내 `get_db`) 이식 완료.

---

## 🛠️ 향후 스프린트 시너지
*   개발팀(동현, 규민, 혜성, 승헌 등)은 조장님이 이식한 DTO 스키마(`app/schemas/`) 및 API 규격을 백본으로 삼아, 2주차 공간 적재 및 RAG 연산을 동일한 규격으로 안심하고 코딩할 수 있게 되었습니다.
