from typing import Optional
from .config import get_route_keywords


def decide_route(*, message: str, explicit_hint: Optional[str] = None) -> str:
    if explicit_hint:
        hint = explicit_hint.strip().lower()
        if hint in {"lmstudio", "gradient", "do"}:
            return hint

    text = (message or "").strip().lower()

    if len(text) > 120:
        return "gradient"

    for kw in get_route_keywords():
        if kw in text:
            return "gradient"

    return "lmstudio"

