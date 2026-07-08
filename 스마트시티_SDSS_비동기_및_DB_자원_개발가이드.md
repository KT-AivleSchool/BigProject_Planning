# ⚙️ [ARCH] 비동기 이벤트 루프 블로킹 회피 및 DB 세션 자원 누수 가이드

이 문서는 스마트시티 SDSS 플랫폼 "OmniSite" 백엔드 개발 시, **FastAPI의 비동기 성능 무결성 보장**과 **DB 커넥션 고갈 예방**을 위한 아키텍처 가이드라인을 팀 전체에 전파하기 위한 기술적 지침서입니다.

---

## 1. ⚡ 이벤트 루프 블로킹 (Event Loop Blocking) 회피

### 📌 문제 정의
FastAPI는 단일 스레드 비동기 루프(Main Event Loop Thread)로 가동됩니다. `bcrypt` 패스워드 암호화 연산이나 대규모 GIS 도형 간 차집합 연산(`ST_Simplify` 등) 같은 CPU-bound 무거운 동기 연산이 이 루프를 직접 타고 흐르면, 연산이 끝날 때까지 서버가 통째로 정지(Freezing)되는 치명적인 대기 병목이 발생합니다.

### 📌 해결 대책
CPU 부하가 큰 무거운 동기 함수들은 반드시 `asyncio.to_thread`를 사용하여 별도의 작업 스레드 풀(Thread Pool Executor)로 안전하게 격리 처리해야 합니다.

#### 💻 구현 가이드라인 (Bcrypt 격리 예시)
```python
import asyncio
import bcrypt

# [OK] Thread Pool로 연산 위임하여 논블로킹(Non-blocking) 보장
salt = await asyncio.to_thread(bcrypt.gensalt)
hashed_pw_bytes = await asyncio.to_thread(
    bcrypt.hashpw,
    password.encode('utf-8'),
    salt
)
hashed_pw = hashed_pw_bytes.decode('utf-8')
```

---

## 2. 🗄️ AsyncSession 커넥션 누수 (Connection Leak) 원천 차단

### 📌 문제 정의
API 요청 가동 중 예외(`HTTPException` 등)나 통신 연결 끊김이 발생하여 트랜잭션 도중 세션 종결(`close`) 처리가 무력화되면, DB 커넥션 풀이 유실되어 서버가 수 시간 내에 뻗게 됩니다.

### 📌 해결 대책
FastAPI의 의존성 주입(`Depends(get_db)`) 제너레이터 패턴의 `finally` 가드를 활용하여, 어떤 예외 상황에서도 `await db.close()`가 100% 호출되도록 자원 해제 생명주기를 완벽히 보증합니다.

#### 💻 deps.py 표준 비동기 가드 구조
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import SessionLocal

async def get_db() -> AsyncSession:
    db = SessionLocal()
    try:
        yield db # 라우터에 비동기 세션 공급
    except Exception:
        await db.rollback() # 트랜잭션 실패 시 즉각 롤백
        raise
    finally:
        await db.close() # API 완료 혹은 에러 차단 시 자원 즉시 100% 반환
```

---

## 🎭 3. 요약: 이벤트 루프 스레드 vs 작업 스레드 (Worker Thread)

*   **이벤트 루프 스레드**: 가벼운 I/O 입출력의 신호를 고속으로 중계하는 **단 1명의 민원실 창구 직원(Main Thread)**.
*   **작업 스레드**: 이벤트 루프가 멈추지 않도록 무거운 CPU 연산을 넘겨받아 백그라운드에서 조용히 수행하는 **스레드 풀 내부의 전문 외주 직원들(ThreadPoolExecutor)**.
