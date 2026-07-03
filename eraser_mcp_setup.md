# 🔌 [MCP 설정 가이드] Eraser.io MCP 서버 연결 및 연동 매뉴얼

본 문서는 사용하시는 AI IDE(Cursor, VS Code 등)에 Eraser.io의 MCP(Model Context Protocol) 서버를 연결하여, AI 에이전트가 다이어그램을 직접 생성/수정/내보내기 하도록 세팅하는 상세 가이드라인입니다.

---

## 💡 1. MCP란 무엇인가요?
Model Context Protocol(MCP)은 AI 모델이 외부 도구(API, 데이터베이스, 웹 서비스 등)와 안전하게 통신할 수 있도록 돕는 개방형 프로토콜입니다. 
Eraser MCP를 연결하면 AI가 **"이 아키텍처 다이어그램 그려줘"**라는 명령어 한 줄만으로 직접 Eraser 계정에 접속하여 정교한 다이어그램을 드로잉해 줍니다.

---

## 🛠️ 2. IDE별 연동 설정 방법 (원격 HTTP 방식 - 가장 간단함)

OAuth 브라우저 로그인 방식을 사용하므로 API 키 발급 없이 **원격 서버 URL**만 입력하면 즉시 동작합니다.

### 1) Cursor (커서) 설정법
1. Cursor 앱을 열고 **`Settings (톱니바퀴)` ➔ `Features` ➔ `MCP`** 섹션으로 이동합니다.
2. **`+ Add New MCP Server`** 버튼을 클릭합니다.
3. 아래 정보를 입력하고 저장합니다:
   * **Name:** `eraser`
   * **Type:** `sse` (또는 `http`)
   * **URL:** `https://app.eraser.io/api/mcp`
4. 연동 후 최초 AI 채팅 시 브라우저가 열리며 Eraser 계정 로그인(OAuth) 인증을 한 번 진행하면 즉시 연동 완료됩니다.

*(또는 `.cursor/mcp.json` 파일에 아래 코드를 직접 추가하셔도 됩니다)*
```json
{
  "mcpServers": {
    "eraser": {
      "url": "https://app.eraser.io/api/mcp"
    }
  }
}
```

### 2) VS Code (Cline / Roo Code / GitHub Copilot) 설정법
VS Code의 MCP 설정 파일(보통 `.vscode/mcp.json` 또는 글로벌 클라이언트 설정)에 아래 블록을 추가합니다.
```json
{
  "inputs": [],
  "servers": {
    "eraser": {
      "url": "https://app.eraser.io/api/mcp",
      "type": "http"
    }
  }
}
```

---

## 🔑 3. API Key를 이용한 로컬 서버 연동 방법 (CLI/로컬형)

만약 OAuth 브라우저 인증이 원활하지 않거나, 오프라인 환경/배치 파이프라인에서 돌리고 싶다면 **API Key 인증 방식**을 사용합니다.

1. [Eraser Account Settings](https://app.eraser.io/) ➔ API Key를 생성 및 복사합니다.
2. 아래와 같이 JSON 설정에 `ERASER_API_KEY`를 환경 변수로 바인딩합니다.

### Cursor / VS Code 로컬 연결 JSON
```json
{
  "mcpServers": {
    "eraser": {
      "command": "npx",
      "args": ["-y", "@eraserlabs/eraser-mcp"],
      "env": {
        "ERASER_API_KEY": "YOUR_ERASER_API_KEY_HERE"
      }
    }
  }
}
```
*(위와 같이 설정해두면 npx가 로컬에서 npm 패키지를 직접 가동해 API Key로 Eraser에 다이렉트 통신합니다)*
