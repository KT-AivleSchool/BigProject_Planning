# 🗄️ OmniSite PostGIS 물리 데이터베이스 설계서 (v1.0.0)

본 설계서는 `스마트시티_SDSS_최종기술명세서 1.md`에 명문화되어 확정되어 있는 **16대 물리 테이블 DDL 설계 규격**입니다. 

DB 파트(임규민 님, 김혜성 님)는 본 설계서의 컬럼명과 타입을 기준으로 `schema.sql`과 Alembic ORM 마이그레이션 코드를 작성해야 합니다.

---

## 🌎 공간 좌표계 및 타입 표준
1.  **좌표계 (SRID)**: **`4326`** (WGS 84 경위도 좌표계 표준화)
2.  **공간 인덱스**: 모든 `GEOMETRY` 공간 컬럼은 성능 튜닝 및 차집합 쿼리 가속을 위해 **`GIST`** 공간 인덱스를 반드시 선언해야 합니다.
3.  **한글 인코딩**: 테이블 및 컬럼은 `UTF-8` 인코딩을 기준으로 적재합니다. (원천 파일 cp949 인코딩은 파이썬 ETL 파이프라인에서 UTF-8로 자동 트랜스레이트 처리)

---

## 📊 테이블별 상세 물리 스키마

### 0. `users` (구정 실무자 계정 마스터)
*   **용도**: 구정 실무자의 보안 인증 및 JWT Access Token 발급용 계정 관리 테이블.

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `email` | VARCHAR(150) | UNIQUE, NOT NULL | 로그인용 이메일 ID |
| `hashed_password` | VARCHAR(255) | NOT NULL | bcrypt 단방향 해싱 암호문 |
| `username` | VARCHAR(100) | NOT NULL | 실무자 이름 |
| `is_active` | BOOLEAN | DEFAULT TRUE | 계정 활성화 상태 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 계정 생성 일시 |

---

### 1. `districts` (자치구역 마스터)
*   **원천 CSV**: `sig.shp` 경계 정보 및 자치구 기본 정보

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `district_name` | VARCHAR(100) | NOT NULL | 예: "서울특별시 용산구" |
| `sig_cd` | VARCHAR(5) | UNIQUE, NOT NULL | 법정 시군구 코드 (예: "11170") |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 시각 |


---

### 2. `dong_boundaries` (서울시 행정동별 공간 정보)
*   **원천 CSV**: `emd.shp` 동별 행정 경계

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `district_id` | INT | REFERENCES districts(id) | 자치구 마스터 외래키 |
| `dong_code` | VARCHAR(10) | UNIQUE, NOT NULL | 행정동 고유 코드 (외래키 조인용) |
| `dong_name` | VARCHAR(100) | NOT NULL | 행정동명 |
| `geom` | GEOMETRY(MultiPolygon, 4326) | GIST INDEX, NOT NULL | 행정동 경계 면 공간 객체 |

---

### 3. `nosmoking_zones` (서울 금연구역 정보)
*   **원천 CSV**: `06. 06-07 금연구역 통합본.csv`

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `district_id` | INT | REFERENCES districts(id) | 자치구 외래키 |
| `dong_id` | INT | REFERENCES dong_boundaries(id) | 행정동 외래키 |
| `zone_name` | VARCHAR(150) | | 시설이름 / 구역명 |
| `address` | VARCHAR(250) | | 주소 |
| `geom` | GEOMETRY(Point, 4326) | GIST INDEX, NOT NULL | Point 좌표 객체 |
| `area` | NUMERIC | | 지정 면적 |
| `registered_at` | DATE | | 지정 일자 |

---

### 4. `childcare_centers` (서울 어린이집/학교 정보)
*   **용도**: 법정 입지 규제(예: 어린이집 반경 200m 이내 입지 차단 등) ST_Difference 차집합 연산용.

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `district_id` | INT | REFERENCES districts(id) | 자치구 외래키 |
| `dong_id` | INT | REFERENCES dong_boundaries(id) | 행정동 외래키 |
| `center_name` | VARCHAR(150) | NOT NULL | 시설명 (어린이집, 유치원, 초등학교 등) |
| `center_type` | VARCHAR(50) | | 시설 종류 구분 |
| `address` | VARCHAR(250) | | 주소 |
| `geom` | GEOMETRY(Point, 4326) | GIST INDEX, NOT NULL | Point 좌표 객체 |
| `student_count` | INT | | 원아/학생 수 |

---

### 5. `transit_stations` (버스/지하철 역사 마스터 위치)
*   **원천 CSV**: `00. 버스정류소 위치.csv` & `02. 지하철역 위치.csv`

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `district_id` | INT | REFERENCES districts(id) | 자치구 외래키 |
| `dong_id` | INT | REFERENCES dong_boundaries(id) | 행정동 외래키 |
| `station_no` | VARCHAR(50) | UNIQUE, NOT NULL | 이용객 조인을 위한 고유 정류소 번호 |
| `station_name` | VARCHAR(150) | NOT NULL | 역사 / 정류소 이름 |
| `transit_type` | VARCHAR(10) | NOT NULL | "BUS" 또는 "SUBWAY" |
| `geom` | GEOMETRY(Point, 4326) | GIST INDEX, NOT NULL | Point 좌표 객체 |

---

### 6. `transit_passengers` (대중교통 이용객 통계)
*   **원천 CSV**: `01. 버스정류소 유동인구.csv` & `03. 지하철역 유동인구.csv`

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `station_id` | INT | REFERENCES transit_stations(id) | 역사 마스터 외래키 |
| `analysis_ym` | VARCHAR(6) | NOT NULL | 분석 년월 (YYYYMM) |
| `boarding_count` | INT | DEFAULT 0 | 승차 승객수 |
| `alighting_count` | INT | DEFAULT 0 | 하차 승객수 |
| `total_volume` | INT | DEFAULT 0 | 총 승하차 승객수 |

---

### 7. `population_stats` (행정동단위 서울 생활인구 통계 요약)
*   **원천 CSV**: `04. 생활인구.csv`

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `dong_id` | INT | REFERENCES dong_boundaries(id) | 행정동 외래키 |
| `day_type` | VARCHAR(10) | NOT NULL | 평일/주말 구분 ("WEEKDAY" / "WEEKEND") |
| `time_type` | VARCHAR(10) | NOT NULL | 시간대 구분 ("RUSH_HOUR" / "DAYTIME" / "NIGHT") |
| `avg_population` | NUMERIC | NOT NULL | 시간대별 평균 생활인구 수 |

---

### 8. `commercial_shops` (소상공인 상가상권 정보)
*   **원천 CSV**: `10. 소상공인시장진흥공단_상가_YONGSAN.csv`

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `district_id` | INT | REFERENCES districts(id) | 자치구 외래키 |
| `dong_id` | INT | REFERENCES dong_boundaries(id) | 행정동 외래키 |
| `shop_name` | VARCHAR(150) | NOT NULL | 상호명 |
| `category_code` | VARCHAR(10) | | 업종 소분류 코드 |
| `category_name` | VARCHAR(50) | | 업종 소분류명 |
| `geom` | GEOMETRY(Point, 4326) | GIST INDEX, NOT NULL | Point 좌표 객체 |

---

### 9. `civil_complaints` (자치구 불법흡연 민원 통계)
*   **용도**: 갈등 민감도 지수(CSS) 공식 연산의 민원 영향도 분석용.

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `dong_id` | INT | REFERENCES dong_boundaries(id) | 행정동 외래키 |
| `complaint_count` | INT | NOT NULL | 불법흡연 관련 민원 신고 건수 |
| `analysis_year` | VARCHAR(4) | NOT NULL | 분석 년도 (YYYY) |

---

### 10. `cadastral_lands` (국토교통부 연속지적도)
*   **용도**: 입지 분석의 대상이 되는 최종 지적 필지 데이터셋.
*   **원천 CSV**: `05. 용산구_도로전체.csv` 및 법정 지적 파일 mapping.

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `district_id` | INT | REFERENCES districts(id) | 자치구 외래키 |
| `dong_id` | INT | REFERENCES dong_boundaries(id) | 행정동 외래키 |
| `pnu` | VARCHAR(19) | NOT NULL | 필지 고유 번호 (19자리 PNU 코드) |
| `jibun` | VARCHAR(100) | | 지번 주소 |
| `land_use_code` | VARCHAR(5) | | 지목 (예: 대, 도로, 체육 등) |
| `ownership_type` | VARCHAR(10) | | 소유 구분 (국유지, 시유지, 사유지 등) |
| `geom` | GEOMETRY(MultiPolygon, 4326) | GIST INDEX, NOT NULL | 다중 폴리곤 통합 공간 객체 |

---

### 11. `trash_bins` (가로휴지통 위치 정보)
*   **원천 CSV**: `11. G1_서울특별시 용산구_가로휴지통_20240630_geocoded.csv`

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `district_id` | INT | REFERENCES districts(id) | 자치구 외래키 |
| `dong_id` | INT | REFERENCES dong_boundaries(id) | 행정동 외래키 |
| `bin_name` | VARCHAR(150) | | 쓰레기통 / 꽁초수거함 이름 |
| `geom` | GEOMETRY(Point, 4326) | GIST INDEX, NOT NULL | Point 좌표 객체 |
| `bin_type` | VARCHAR(50) | | 휴지통 종류 구분 |

---

### 12. `age_demographics` (주민등록인구 연령별 동별 통계)
*   **용도**: 만 19세 미만 청소년 인구 밀집도 계산(갈등 민감도 감점 요인)용.

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `dong_id` | INT | REFERENCES dong_boundaries(id) | 행정동 외래키 |
| `youth_population` | INT | NOT NULL | 만 19세 미만 청소년 인구 수 |
| `total_population` | INT | NOT NULL | 행정동 총 거주인구 수 |
| `youth_ratio` | NUMERIC | NOT NULL | 청소년 인구 비율 (youth / total) |

---

### 13. `cigarette_dumping_zones` (담배꽁초상습무단투기지역현황)
*   **원천 CSV**: `07. 담배꽁초_상습_무단투기.csv`

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `district_id` | INT | REFERENCES districts(id) | 자치구 외래키 |
| `dong_id` | INT | REFERENCES dong_boundaries(id) | 행정동 외래키 |
| `address` | VARCHAR(250) | | 도로명 / 지번 주소 |
| `detail_location` | TEXT | | 상세 지점 묘사 |
| `geom` | GEOMETRY(Point, 4326) | GIST INDEX, NOT NULL | 상습 투기 지점 좌표 포인트 |

---

### 14. `ahp_models` (AHP 가중치 프로파일 마스터)
*   **용도**: 사용자가 검증 완료 후 락(Lock)을 건 AHP 세트 동결 저장용.

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `district_id` | INT | REFERENCES districts(id) | 자치구 외래키 |
| `criteria_weights` | JSONB | NOT NULL | 5대 인자별 가중치 수치 매트릭스 JSON 백업 |
| `consistency_ratio` | NUMERIC | NOT NULL | 일관성 비율 값 (C.R. < 0.1 검증필) |
| `is_locked` | BOOLEAN | DEFAULT FALSE | 의사결정 모델 영구 락 여부 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 시각 |

---

### 15. `conflict_simulations` (시뮬레이션 결과 리포트 캐시)
*   **용도**: GPT-4o 모의 토론 내용 및 갈등 민감도(CSS) 분석 결과 아카이빙.

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `cadastral_land_id` | INT | REFERENCES cadastral_lands(id) | 선정 지적 필지 외래키 |
| `css_score` | NUMERIC | NOT NULL | 종합 갈등 민감도 점수 (CSS) |
| `css_vector` | JSONB | NOT NULL | 상세 갈등 민감도 지표 인자 정보 백업 |
| `normal_scenario` | TEXT | | 일반 시나리오 A 모의 토론 로그 전문 |
| `optimal_scenario` | TEXT | | 우호적 타결 시나리오 B 모의 토론 로그 전문 |
| `worst_scenario` | TEXT | | 극단적 불합의 시나리오 C 모의 토론 로그 전문 |
| `confidence_score` | NUMERIC | | AI 분석 신뢰성 점수 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 시각 |

---

### 16. `verified_precedents` (Audit AI 실증 이행 사례 기록)
*   **용도**: PDF 준공 검증을 필터링 통과한 실제 이행 결과 RAG 순환 수집용 (격리 세그먼트).

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | DB 고유 ID |
| `conflict_simulation_id` | INT | REFERENCES conflict_simulations(id) | 원천 가상 시뮬레이션 매핑 외래키 |
| `document_title` | VARCHAR(250) | | 행정 공문서 제목 |
| `document_ocr_text` | TEXT | | OCR로 추출 완료된 공문 내용 원문 |
| `actual_scenario` | VARCHAR(50) | NOT NULL | 실제 도달 시나리오 판정 유형 ('NORMAL', 'OPTIMAL', 'WORST') |
| `verified_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 검증/저장 시각 |
