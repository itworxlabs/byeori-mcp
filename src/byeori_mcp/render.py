"""벼리가 준 결과를 LLM 이 읽을 글로 바꾼다.

JSON 으로 주면 LLM 이 필드 이름을 출처로 옮기거나 빠뜨린다 — 파일 이름과 쪽을 글 안에 넣는다.
file.id 와 matched_by 는 넣지 않는다 — LLM 에게 쓸모가 없고 토큰만 쓴다.
"""

from collections.abc import Sequence

from byeori_mcp.byeori import Hit

# 0건이어도 빈 글을 주지 않는다 — LLM 은 빈 결과를 받으면 자기 기억으로 답한다
NOTHING_FOUND = "관련된 내용을 찾지 못했습니다. 이 질문은 사내 문서를 찾지 못한 채 답하지 마세요."


def _pages(hit: Hit) -> str:
    """쪽이 없는 형식이 있다(HWPX) — 없으면 적지 않는다. '(None쪽)' 이 되지 않게."""
    if hit.page_start is None:
        return ""
    if hit.page_end is None or hit.page_end == hit.page_start:
        return f" ({hit.page_start}쪽)"
    return f" ({hit.page_start}~{hit.page_end}쪽)"


def render(hits: Sequence[Hit]) -> str:
    if not hits:
        return NOTHING_FOUND
    parts = [f"[{i}] {h.file_name}{_pages(h)}\n{h.text}" for i, h in enumerate(hits, 1)]
    return "\n\n".join(parts)
