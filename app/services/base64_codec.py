"""Base64 编解码核心逻辑。"""

import base64
import binascii
from typing import Final


SUPPORTED_ENCODINGS: Final = ("UTF-8", "GBK")


class Base64CodecError(ValueError):
    """Base64 编解码失败。"""


def encode_text(text: str, encoding: str = "UTF-8", url_safe: bool = False) -> str:
    """把文本编码为 Base64 字符串。"""
    try:
        raw = text.encode(encoding)
    except (LookupError, UnicodeEncodeError) as exc:
        raise Base64CodecError(f"无法使用 {encoding} 编码当前文本：{exc}") from exc

    encoder = base64.urlsafe_b64encode if url_safe else base64.b64encode
    return encoder(raw).decode("ascii")


def decode_text(
    value: str,
    encoding: str = "UTF-8",
    url_safe: bool = False,
    fix_padding: bool = True,
) -> str:
    """把 Base64 字符串解码为文本。"""
    compact_value = "".join(value.split())
    if not compact_value:
        return ""

    try:
        encoded = compact_value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise Base64CodecError("Base64 内容只能包含 ASCII 字符") from exc

    if fix_padding:
        encoded += b"=" * (-len(encoded) % 4)

    try:
        if url_safe:
            raw = base64.b64decode(encoded, altchars=b"-_", validate=True)
        else:
            raw = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise Base64CodecError(f"输入不是有效的 Base64 内容：{exc}") from exc

    try:
        return raw.decode(encoding)
    except (LookupError, UnicodeDecodeError) as exc:
        raise Base64CodecError(f"解码结果不是有效的 {encoding} 文本：{exc}") from exc
