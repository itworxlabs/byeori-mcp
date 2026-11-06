"""환경변수 넷 — 하나라도 없으면 서버가 뜨지 않는다.

늦게 실패하면 설정 잘못이 "자료가 없음" 으로 둔갑한다 — LLM 이 빈 결과를 받아 자기 기억으로 지어낸다.
"""

import os
from dataclasses import dataclass

NAMES = ("BYEORI_URL", "BYEORI_API_KEY", "BYEORI_KB_ID", "BYEORI_KB_DESCRIPTION")


class MissingSettings(RuntimeError):
    """무엇이 없는지 이름을 적어 알린다. 값은 적지 않는다 — 키가 섞인다."""


@dataclass(frozen=True)
class Settings:
    url: str
    api_key: str
    kb_id: str
    kb_description: str

    @property
    def search_url(self) -> str:
        return f"{self.url.rstrip('/')}/external/v1/knowledge-bases/{self.kb_id}/search"


def load(environ: dict[str, str] | None = None) -> Settings:
    env = os.environ if environ is None else environ
    values = {name: (env.get(name) or "").strip() for name in NAMES}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise MissingSettings("환경변수가 없어 시작할 수 없다: " + " · ".join(missing))
    return Settings(
        url=values["BYEORI_URL"],
        api_key=values["BYEORI_API_KEY"],
        kb_id=values["BYEORI_KB_ID"],
        kb_description=values["BYEORI_KB_DESCRIPTION"],
    )
