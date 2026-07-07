# 🛡️ OmniSite 프로젝트 트랙별 독립 병렬 개발 현황 명세 (ADR-003)

본 문서는 스마트시티 SDSS 플랫폼 **OmniSite**의 개발 생산성을 극대화하기 위해, **메인 협업 개발 트랙**과 **조장 배종현 님의 단독 R&D 트랙**을 완벽하게 격리하여 병렬 운영하는 아키텍처 및 형상관리 정책을 수립한 기술 명세입니다.

---

## 📄 형상 관리 분리 정책 (Branch & Folder Isolation)
*   **배경**: 메인 개발팀의 풀스택 SSE 연동 및 비동기 DB 인프라 작업 영역과, 조장 배종현 님의 조례 PDF 관리창구/Deletion Engine 단독 구현 레이어가 서로 상호 충돌(Conflict)을 일으키지 않도록 격리합니다.
*   **운영 원칙**: 
    1.  **메인 협업 트랙**의 산출물은 레포지토리 루트(`backend/`, `frontend/`, 마스터 기획 문서)에 등재합니다.
    2.  **조장 단독 트랙**의 산출물은 루트 하위의 격리 백업 디렉토리인 `[조장_단독_진행_0706/](file:///Users/jcm0314/Downloads/빅프로젝트/조장_단독_진행_0706)` 상에 온전히 보존하며, 메인 협업 소스코드 브랜치에 직접 강제 덮어쓰기(Overwrite)하지 않습니다.

---

## 🗺️ 2대 병렬 개발 트랙 진행 현황판

```
[OmniSite 마스터 레포지토리]
       │
       ├─► 🛠️ [트랙 1] 메인 협업 개발 트랙 (장천명, 찬진, 동현, 규민, 혜성, 승헌)
       │    └─ Next.js - FastAPI SSE 스트리밍 토론 채널 연동 마감
       │    └─ Docker PostgreSQL/PostGIS 로컬 DB 기동 및 비동기 SQLAlchemy 2.0 세션 포팅
       │
       └─► ⚖️ [트랙 2] 조장 단독 R&D 트랙 (배종현) ── [격리 디렉토리 보존]
            └─ 조례 PDF 독립 다중 업로드 모달 분리 창구 구현
            └─ 조례 중복 방지 가드 (400 Bad Request) 및 물리 캐시 삭제 엔진 (Deletion Engine)
```

### 1️⃣ [트랙 1] 메인 협업 개발 트랙 (현행화 상태)
*   **스프린트 목표**: 1주차 핵심 E2E 채널(SSE) 연동 및 로컬 가상화 공간 DB 인프라 구축.
*   **완료 피처**:
    *   FastAPI의 `EventSourceResponse` 기반 실시간 토론 대사 1.5초 간격 스트리밍.
    *   토론 종결(`is_finished`) 검출 즉시 결과 통계 API(`/results`) 연쇄 동적 Fetch 바인딩.
    *   `docker compose` 기반 PostGIS + pgvector 통합 컨테이너 구동 성공 및 SQLAlchemy 2.0 비동기 헬퍼(`get_db`) 포팅 완료.
*   **주요 소스**: `backend/app/api/v1/simulations.py`, `backend/app/db/session.py`, `frontend/src/app/page.js`

### 2️⃣ [트랙 2] 조장 단독 R&D 트랙 (독립 보존 상태)
*   **스프린트 목표**: RAG 조례 PDF 창구 독립 모달 분리 및 중복 방지, 개별 물리 파일/캐시 소거 검증.
*   **완료 피처**:
    *   메인 판넬 우측의 RAG 업로더를 상단 헤더의 `[⚖️ 법규 RAG 관리]` 전용 모달 창구로 격리 분리.
    *   `GET /upload/regulations` API 기반 조례 목록 독립 팝업 조회 리스팅.
    *   동일 파일명 PDF 재적재 시 RAG 중복 방지 가드(400 Bad Request) 작동.
    *   `DELETE /upload/regulations/{filename}` 호출 시 원본 PDF와 텍스트 추출 캐시(`[파일명].txt`) 물리 동시 소거.
*   **산출물 경로**: [조장_단독_진행_0706/](file:///Users/jcm0314/Downloads/빅프로젝트/조장_단독_진행_0706) 하위 아카이브

---

## 🛠️ 기대 효과 및 상호 시너지
*   메인 개발팀은 조장님의 변경 코드로 인한 의존성 이격 리스크 없이, 안정적으로 PostGIS 공간 쿼리와 RAG 프롬프트를 2주차에 이식할 수 있습니다.
*   조장님의 Deletion Engine과 중복 가드 기능은 향후 EKS 상용 배포 및 마이크로서비스 격리(2단계 배포 프로세스) 시점에 독립 패키지로 깔끔하게 병합 이식될 예정입니다.
