"""벼리를 부르는 코드 — 전송 방식(stdio)과 섞지 않는다.

나중에 HTTP 로 넓힐 때 고칠 자리가 한 곳이어야 한다.
"""

from dataclasses import dataclass

import httpx2

from byeori_mcp.settings import Settings

TIMEOUT_SECONDS = 30.0


@dataclass(frozen=True)
class Hit:
    text: str
    file_name: str
    page_start: int | None
    page_end: int | None


class ByeoriError(RuntimeError):
    """LLM 에게 그대로 보여줄 글을 들고 있다 — 사람이 읽을 글이어야 한다."""


# 벼리가 돌려준 본문은 넣지 않는다 — 키가 되돌아올 수 있다
_UNAUTHORIZED = (
    "벼리 인증에 실패했습니다. API 키를 확인하세요. "
    "이 질문은 사내 문서를 찾지 못한 채 답하지 마세요."
)
_NOT_FOUND = "이 키로 볼 수 있는 KB 가 아닙니다."


def search(
    settings: Settings, query: str, limit: int, client: httpx2.Client | None = None
) -> list[Hit]:
    own = client is None
    http = client or httpx2.Client(timeout=TIMEOUT_SECONDS)
    try:
        response = http.post(
            settings.search_url,
            headers={"Authorization": f"Bearer {settings.api_key}"},
            json={"query": query, "limit": limit},
        )
    except httpx2.HTTPError as exc:
        raise ByeoriError(
            f"벼리에 닿지 못했습니다({type(exc).__name__}). "
            "이 질문은 사내 문서를 찾지 못한 채 답하지 마세요."
        ) from exc
    finally:
        if own:
            http.close()
    if response.status_code == 401:
        raise ByeoriError(_UNAUTHORIZED)
    if response.status_code == 404:
        raise ByeoriError(_NOT_FOUND)
    if response.status_code != 200:
        # 본문은 넣지 않는다 — 보낸 글이나 키가 되돌아올 수 있다
        raise ByeoriError(
            f"벼리가 {response.status_code} 로 응답했습니다. "
            "이 질문은 사내 문서를 찾지 못한 채 답하지 마세요."
        )
    items = response.json().get("items", [])
    return [
        Hit(
            text=item["text"],
            file_name=item["file"]["name"],
            page_start=item.get("page_start"),
            page_end=item.get("page_end"),
        )
        for item in items
    ]
