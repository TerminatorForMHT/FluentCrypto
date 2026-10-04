"""随机密码生成服务。"""

import math
import secrets
import string
from typing import Final, Tuple


MIN_LENGTH: Final = 4
MAX_LENGTH: Final = 128
DEFAULT_LENGTH: Final = 16
AMBIGUOUS_CHARS: Final = "0O1lI"
SYMBOL_CHARS: Final = "!@#$%^&*()-_=+[]{};:,.<>?/"


class PasswordError(ValueError):
    """密码生成失败。"""


def generate_password(
    length: int = DEFAULT_LENGTH,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> str:
    """生成随机密码；长度允许时保证每类已选字符至少出现一次。"""
    if not MIN_LENGTH <= length <= MAX_LENGTH:
        raise PasswordError(f"密码长度需在 {MIN_LENGTH}~{MAX_LENGTH} 之间")
    charset, groups = _build_charset(
        use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous
    )
    while True:
        password = "".join(secrets.choice(charset) for _ in range(length))
        if len(groups) > length:
            return password
        if all(any(char in group for char in password) for group in groups):
            return password


def estimate_strength(
    length: int,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> Tuple[str, int]:
    """按字符池估算熵，返回（强度等级, 熵位数）。"""
    charset, _ = _build_charset(
        use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous
    )
    bits = int(length * math.log2(len(charset)))
    if bits < 50:
        return "弱", bits
    if bits < 80:
        return "中", bits
    return "强", bits


def _build_charset(
    use_upper: bool,
    use_lower: bool,
    use_digits: bool,
    use_symbols: bool,
    exclude_ambiguous: bool,
) -> Tuple[str, Tuple[str, ...]]:
    groups = []
    if use_lower:
        groups.append(string.ascii_lowercase)
    if use_upper:
        groups.append(string.ascii_uppercase)
    if use_digits:
        groups.append(string.digits)
    if use_symbols:
        groups.append(SYMBOL_CHARS)
    if exclude_ambiguous:
        groups = [
            "".join(char for char in group if char not in AMBIGUOUS_CHARS)
            for group in groups
        ]
    groups = [group for group in groups if group]
    if not groups:
        raise PasswordError("请至少选择一种可用字符集")
    return "".join(groups), tuple(groups)
