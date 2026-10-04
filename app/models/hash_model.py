"""哈希计算模型。"""

from dataclasses import dataclass
from typing import Tuple

from app.services.hash_service import (
    HASH_ALGORITHMS,
    SUPPORTED_TEXT_ENCODINGS,
    calculate_hash,
    verify_hash,
)


@dataclass(frozen=True)
class HashOptions:
    """哈希计算选项。"""

    algorithm: str = "SHA-256"
    encoding: str = "UTF-8"
    hmac_key: str = ""


class HashModel:
    """维护哈希选项并执行计算与验证。"""

    def __init__(self) -> None:
        self._options = HashOptions()

    @property
    def algorithms(self) -> Tuple[str, ...]:
        return tuple(HASH_ALGORITHMS.keys())

    @property
    def text_encodings(self) -> Tuple[str, ...]:
        return SUPPORTED_TEXT_ENCODINGS

    def configure(self, algorithm: str, encoding: str, hmac_key: str) -> None:
        self._options = HashOptions(algorithm, encoding, hmac_key)

    def calculate(self, text: str) -> str:
        return calculate_hash(
            text,
            self._options.algorithm,
            self._options.encoding,
            self._options.hmac_key,
        )

    def verify(self, text: str, expected: str) -> bool:
        return verify_hash(
            text,
            expected,
            self._options.algorithm,
            self._options.encoding,
            self._options.hmac_key,
        )
