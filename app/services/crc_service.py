"""CRC 计算与验证服务。"""

from typing import Dict, Final, Type

from crccheck.crc import (
    Crc8,
    Crc16CcittFalse,
    Crc16Modbus,
    Crc32C,
    Crc32IsoHdlc,
    Crc64Ecma182,
)


class CrcError(ValueError):
    """CRC 操作失败。"""


CRC_ALGORITHMS: Final[Dict[str, Type]] = {
    "CRC-8": Crc8,
    "CRC-16/MODBUS": Crc16Modbus,
    "CRC-16/CCITT-FALSE": Crc16CcittFalse,
    "CRC-32/ISO-HDLC": Crc32IsoHdlc,
    "CRC-32C": Crc32C,
    "CRC-64/ECMA-182": Crc64Ecma182,
}


def calculate_crc(text: str, algorithm: str, encoding: str = "UTF-8") -> int:
    """计算文本的 CRC 整数值。"""
    crc_class = CRC_ALGORITHMS.get(algorithm)
    if crc_class is None:
        raise CrcError(f"不支持的 CRC 算法：{algorithm}")
    try:
        data = text.encode(encoding)
    except (LookupError, UnicodeEncodeError) as exc:
        raise CrcError(f"文本无法使用 {encoding} 编码：{exc}") from exc
    return int(crc_class.calc(data))


def format_crc(value: int, algorithm: str) -> str:
    """格式化 CRC 为固定宽度大写 Hex 和十进制。"""
    crc_class = CRC_ALGORITHMS.get(algorithm)
    if crc_class is None:
        raise CrcError(f"不支持的 CRC 算法：{algorithm}")
    width = int(crc_class.width()) // 4
    return f"0x{value:0{width}X}\n十进制：{value}"


def parse_expected_crc(value: str, algorithm: str) -> int:
    """解析十六进制或十进制期望 CRC。"""
    text = value.strip().replace("_", "")
    if not text:
        raise CrcError("请输入期望 CRC")
    try:
        if text.lower().startswith("0x"):
            result = int(text, 16)
        elif any(char in "abcdefABCDEF" for char in text):
            result = int(text, 16)
        else:
            result = int(text, 10)
    except ValueError as exc:
        raise CrcError("期望 CRC 必须是十进制或十六进制整数") from exc

    crc_class = CRC_ALGORITHMS.get(algorithm)
    if crc_class is None:
        raise CrcError(f"不支持的 CRC 算法：{algorithm}")
    maximum = (1 << int(crc_class.width())) - 1
    if not 0 <= result <= maximum:
        raise CrcError(f"期望 CRC 超出 {crc_class.width()} 位范围")
    return result


def verify_crc(
    text: str,
    expected: str,
    algorithm: str,
    encoding: str = "UTF-8",
) -> bool:
    """验证文本 CRC 是否与期望值一致。"""
    return calculate_crc(text, algorithm, encoding) == parse_expected_crc(
        expected, algorithm
    )
