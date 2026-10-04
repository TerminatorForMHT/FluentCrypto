"""CRC 校验模型。"""

from dataclasses import dataclass
from typing import Tuple

from app.services.crc_service import CRC_ALGORITHMS, calculate_crc, format_crc, verify_crc
from app.services.symmetric_crypto import SUPPORTED_TEXT_ENCODINGS


@dataclass(frozen=True)
class CrcOptions:
    """CRC 计算选项。"""

    algorithm: str = "CRC-32/ISO-HDLC"
    encoding: str = "UTF-8"


class CrcModel:
    """维护 CRC 状态并执行计算与验证。"""

    def __init__(self) -> None:
        self._options = CrcOptions()

    @property
    def algorithms(self) -> Tuple[str, ...]:
        return tuple(CRC_ALGORITHMS.keys())

    @property
    def text_encodings(self) -> Tuple[str, ...]:
        return SUPPORTED_TEXT_ENCODINGS

    def configure(self, algorithm: str, encoding: str) -> None:
        self._options = CrcOptions(algorithm, encoding)

    def calculate(self, text: str) -> str:
        value = calculate_crc(text, self._options.algorithm, self._options.encoding)
        return format_crc(value, self._options.algorithm)

    def verify(self, text: str, expected: str) -> bool:
        return verify_crc(
            text,
            expected,
            self._options.algorithm,
            self._options.encoding,
        )
