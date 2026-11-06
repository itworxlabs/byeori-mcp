# 벼리 MCP 서버

LLM 이 벼리의 KB 를 직접 찾아 쓰게 하는 MCP 서버다.
이 글은 쓰는 법만 적는다.

## 무엇을 내놓나

도구 하나다.

```
search_byeori(query, limit=10)  →  파일 이름과 쪽이 붙은 글
```

KB 와 그 설명은 도구의 인자가 아니라 **환경변수**다. LLM 은 UUID 를 정확히 옮기지 못하고,
고정된 설명으로는 언제 부를지 판단하지 못한다.

## 환경변수 넷 — 하나라도 없으면 서버가 뜨지 않는다

| 이름 | 값 |
| --- | --- |
| `BYEORI_URL` | 벼리 주소. 예 `http://127.0.0.1:8000` |
| `BYEORI_API_KEY` | 그 앱의 API 키. 벼리의 **API 키** 화면에서 발급한다 |
| `BYEORI_KB_ID` | 볼 KB 의 번호(UUID). KB 관리 화면의 주소에 있다 |
| `BYEORI_KB_DESCRIPTION` | **LLM 이 읽을 KB 설명.** 무엇이 든 KB 인지 적는다 |

마지막 값이 중요하다. *"사내 문서를 검색한다"* 처럼 적으면 LLM 이 아무 질문에나 부르거나
필요할 때 안 부른다. 예: `"월별 수출입동향 보고서. 품목별 · 국가별 수출입 실적과 증감률."`

## 붙이는 법

`.mcp.json`(Claude Code) 또는 그 LLM 앱의 MCP 설정에 아래를 넣는다.
**이 파일은 저장소에 넣지 않는다**(`.gitignore`) — 키가 들어 있고, 환경변수를 안 가진 사람에게는
매번 실패하는 서버가 하나 생긴다.

```json
{
  "mcpServers": {
    "byeori": {
      "command": "uv",
      "args": ["run", "--directory", "apps/mcp", "byeori-mcp"],
      "env": {
        "BYEORI_URL": "<벼리 주소>",
        "BYEORI_API_KEY": "<발급받은 키>",
        "BYEORI_KB_ID": "<KB 번호>",
        "BYEORI_KB_DESCRIPTION": "<이 KB 가 무엇을 담았는지 한두 문장>"
      }
    }
  }
}
```

**네 값을 직접 적는다.** 처음에는 `"${BYEORI_URL}"` 처럼 환경변수 이름으로 적었는데 **그 꼴은
데스크톱 앱에서 통하지 않는다** — macOS 의 GUI 앱은 `~/.zshrc` 를 읽지 않아, 터미널에 `export` 해
두어도 앱이 띄운 서버에는 전달되지 않는다(2026-11-05 실제로 겪었다). 터미널에서 띄우는 경우에만
환경변수 참조가 통한다.

**키가 든 파일이므로 권한을 600 으로 둔다.**

`--directory` 는 이 저장소 기준의 상대 경로다. 저장소 밖에서 쓰면 절대 경로로 바꾼다.

**키를 명령 인자로 넘기지 않는다** — 같은 PC 의 다른 프로그램이 `ps` 로 본다.

같은 설명이 벼리 포털의 가이드 화면에도 있다. 한쪽을 고치면 다른 쪽도 함께 본다.

## 검사

```bash
uv run pytest        # 계약 · 글 바꾸기 · 키 새지 않기
uv run ruff check .
uv run mypy
```

CI 는 백엔드 작업 안에서 이 넷을 돌린다(작업을 따로 만들지 않는다).
되돌려 보기는 저장소 맨 위에서 `python3 scripts/mutate.py apps/mcp/mutations.yaml` — 모두 "실패함" 이어야 한다.
