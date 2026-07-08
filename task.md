# 📋 PostGIS DB 인프라 및 비동기 SQLAlchemy 팩토리 구축 TODO 리스트

- [x] 로컬 공간 DB 자동화 셋업용 `docker-compose.yml` 작성
- [x] 16대 물리 테이블 생성용 `schema.sql` 스크립트 작성
- [x] 백엔드 `session.py` 비동기(asyncpg) 세션 및 `get_db` 주입 모듈 리팩토링
- [x] 로컬 Docker DB 컨테이너 기동 및 schema.sql 테이블 주입 테스트
- [x] 조장(배종현) 단독 고도화 API DTO 및 RAG Deletion Engine 통합 반영 및 push 완료
- [x] 프론트엔드 및 백엔드 마스터 브랜치에 조례 RAG 관리 4대 피처 완벽 병합 이식 완료
- [x] 프로젝트 선행 개발 가이드라인 기반 협업 정책 명문화 (`OMNISITE_WORKSPACE_TRACKS.md` 배포 완료)
- [x] 로컬 연동 자가 검증 및 Walkthrough 업데이트
- [x] **[2차 피벗]** Step 1 CSV 전용 AI 감리 API 구현 및 가중치/의도 로컬 격리 보존
- [x] **[3차 피벗]** Step 2 하이브리드 HITL(공간 마커 물리 드래그 보정 + 탐색의도 텍스트 편집) 통합 구현 및 DB 커밋 연동 완료
- [x] **[2차 피벗]** Step 3 동적으로 도출된 가중치 인자 리스트 슬라이더 매핑 및 AHP N x N 상대 행렬 연산 연동 완료
