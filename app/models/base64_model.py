"""Base64 编解码模型。"""

from dataclasses import dataclass
from typing import Tuple

from app.services.base64_codec import (
    Base64CodecError,
    SUPPORTED_ENCODINGS,
    decode_text,
    encode_text,
)


@dataclass(frozen=True)
class CodecOptions:
    """编解码选项。"""

    encoding: str = "UTF-8"
    url_safe: bool = False
    fix_padding: bool = True


class Base64Model:
    """保存应用状态并提供 Base64 编解码能力。"""

    def __init__(self) -> None:
        self._options = CodecOptions()

    @property
    def supported_encodings(self) -> Tuple[str, ...]:
        return SUPPORTED_ENCODINGS

    @property
    def options(self) -> CodecOptions:
        return self._options

    def configure(
        self,
        encoding: str,
        url_safe: bool,
        fix_padding: bool,
    ) -> None:
        if encoding not in self.supported_encodings:
            raise Base64CodecError(f"不支持的字符编码：{encoding}")
        self._options = CodecOptions(encoding, url_safe, fix_padding)

    def encode(self, text: str) -> str:
        return encode_text(
            text,
            encoding=self._options.encoding,
            url_safe=self._options.url_safe,
        )

    def decode(self, value: str) -> str:
        return decode_text(
            value,
            encoding=self._options.encoding,
            url_safe=self._options.url_safe,
            fix_padding=self._options.fix_padding,
        )
