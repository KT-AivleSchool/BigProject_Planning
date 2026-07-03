# 📅 [제출용] Weekly Scrum 1주차 완료 보고서 (v1.0.0-prototype)

본 문서는 **"9기 빅프로젝트 산출물 워크시트(AI트랙)"** 4페이지에 수록해야 하는 **1주차 Weekly Scrum**의 공식 제출용 텍스트 명세입니다.

---

## 📋 [과제 심의] Weekly Scrum Template (1주차)

| 분야 | 이번주 한 일 (Done) | 차주 계획 (Todo) | 이슈사항 (Issues) |
| :--- | :--- | :--- | :--- |
| **AI** | - LangGraph 기반 3자 페르소나 모의 토론 및 [일반/우호/불합의] 3대 시나리오 분기 흐름 정의<br>- 가상 결과 재유입 시 RAG 오염(Model Collapse) 방지를 위한 **Audit AI(OCR 팩트체크)** 피드백 아키텍처 구상<br>- GPT-4o API 단가 절감을 위한 Top 1~3 온디맨드 API 요금 및 프롬프트 캐싱 설계 | - LangGraph 에이전트(주민, 상인, 공무원) 상태 노드 및 전이 그래프 코드 설계<br>- RAG 조례 문서 청킹 및 임베딩을 위한 pgvector/Chroma DB 연동 테스트 | - GPT-4o-mini 수준 모델 사용 시 페르소나 붕괴 및 조기 타협 문제 확인 ➔ 고성능 추론 모델(GPT-4o) 고정 및 호출 횟수 제한 로직 적용 필요 |
| **Web** | - Next.js 기반 단일 프론트엔드 프로젝트 스켈레톤 구조 확립<br>- Mapbox GL JS 공간 시각화 라이브러리 선정 및 GIS 마스크 폴리곤 렌더링 스키마 정의<br>- 일괄 파일 드래그앤드롭 드롭존 및 실시간 SSE 토론 스트리밍 UI 와이어프레임 설계 | - Next.js + Mapbox GL JS 융합 및 시범 구역(용산구) 경계 폴리곤 렌더링 검증<br>- 드래그앤드롭 일괄 업로드 및 Visual HITL 핀 드래그 조정 컴포넌트 UI 구현 | - 1주차 Next.js 구성 및 컴포넌트 레이아웃 수립 |
| **BackEnd** | - Python FastAPI 단일 통합형 백엔드(Monolith) 전환 및 라우터 설계<br>- AHP(쌍대비교) 일관성 비율(C.R. < 0.1) 검증 수식 정의 및 AHP 모델 Lock 테이블 설계<br>- PostgreSQL/PostGIS 13종 물리 테이블 스키마 및 GIST 공간 인덱싱 아키텍처 모델링 | - PostgreSQL/PostGIS 데이터베이스 마이그레이션 및 13종 DDL 스키마 적용<br>- 업로드 파일 분기 파서 및 결측치 주소 Vworld API 기반 지오코딩 API 구현<br>- AHP C.R. 계산 및 DB 락인(Lock) API 개발 | - FastAPI와 Next.js 간의 로컬 포트 CORS 문제 조율 및 Server-Sent Events(SSE) 스트리밍 지연 방지 처리 필요 |
| **데이터** | - MVP 데이터 수집(용산구 연속지적도, 버스정류소, 학교, 상가 등 실물 데이터 19종 수집 완료)<br>- 수집 데이터셋 간의 정량적 정합성 및 공간 속성 컬럼 매핑 검증<br>- HWP/PDF 조례 원천 데이터 청크화 사전 정제 및 1차 가공 완료 | - 1차 가공 데이터의 좌표계 투영 변환 (`EPSG:4326` WGS84 단일화)<br>- PostGIS `ST_Difference` 연산을 위한 제한/보호구역 버퍼 공간 데이터 마스킹 파일 생성 | - 데이터셋 간의 원천 좌표계가 경위도(WGS84) 및 평면직각좌표계(GRS80)로 혼재되어 있어 정밀 투영 변환 선행 필요 |
| **발표 및 자료 작성** | - GitHub 레포지토리 구성 및 8주 스프린트 WBS R&R 마일스톤 확립<br>- 1주차 연구노트 작성 및 아이디어 기획서 구성<br>- E2E 5단계 파이프라인 및 시스템 아키텍처(Next-FastAPI Monolith) 기술 설계서 작성 | - 조별 과제정의서 최종본 마감 및 제출 준비<br>- 서비스 플로우(흐름도) 렌더링 및 UI/UX 핵심 프레임 설계서 슬라이드 작성 | - 특이사항 없음 |
