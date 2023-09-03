__all__ = ("bool_to_str", "join_code")

from collections.abc import Iterable


def bool_to_str(condition: bool) -> str:
    return "はい" if condition else "いいえ"


def join_code(
    texts: Iterable[str], inner_text: str = ", ", null_text: str = "なし"
) -> str:
    if not (joined := f"`{inner_text}`".join(texts)):
        return null_text
    return f"`{joined}`"
