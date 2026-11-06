"""MCP 서버 — 도구 하나(search_byeori)를 stdio 로 내놓는다.

벼리를 부르는 것은 byeori.py, 글로 바꾸는 것은 render.py 다 — 전송 방식과 섞지 않는다.
"""

import sys

from mcp.server.mcpserver import MCPServer

from byeori_mcp import byeori, render
from byeori_mcp.settings import MissingSettings, Settings, load

LIMIT_DEFAULT = 10
LIMIT_MAX = 20  # 벼리 외부 검색 API 가 받는 상한


def build(settings: Settings) -> MCPServer:
    # description 은 환경변수로 받는다 — LLM 은 이 글만 보고 부를지 정한다
    server = MCPServer("byeori")

    @server.tool(name="search_byeori", description=settings.kb_description)
    def search_byeori(query: str, limit: int = LIMIT_DEFAULT) -> str:
        """사내 문서에서 질문과 관련된 문단을 찾는다."""
        try:
            hits = byeori.search(settings, query, min(max(limit, 1), LIMIT_MAX))
        except byeori.ByeoriError as exc:
            return str(exc)  # 사람이 읽을 글 — LLM 이 사용자에게 옮긴다
        return render.render(hits)

    return server


def main() -> int:
    try:
        settings = load()
    except MissingSettings as exc:
        print(str(exc), file=sys.stderr)
        return 2
    build(settings).run(transport="stdio")
    return 0


if __name__ == "__main__":
    sys.exit(main())
