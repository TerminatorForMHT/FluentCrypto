"""哈希与 HMAC 计算服务。"""

import hashlib
import hmac
from typing import Dict, Final, Tuple


SUPPORTED_TEXT_ENCODINGS: Final[Tuple[str, ...]] = ("UTF-8", "GBK")

HASH_ALGORITHMS: Final[Dict[str, str]] = {
    "MD5": "md5",
    "SHA-1": "sha1",
    "SHA-224": "sha224",
    "SHA-256": "sha256",
    "SHA-384": "sha384",
    "SHA-512": "sha512",
    "SHA3-256": "sha3_256",
    "SHA3-512": "sha3_512",
    "BLAKE2b": "blake2b",
    "BLAKE2s": "blake2s",
}

INSECURE_ALGORITHMS: Final[Tuple[str, ...]] = ("MD5", "SHA-1")


class HashError(ValueError):
    """哈希计算失败。"""


def calculate_hash(
    text: str,
    algorithm: str,
    encoding: str = "UTF-8",
    hmac_key: str = "",
) -> str:
    """计算文本哈希（可带 HMAC 密钥），返回大写十六进制摘要。"""
    digest_name = HASH_ALGORITHMS.get(algorithm)
    if digest_name is None:
        raise HashError(f"不支持的哈希算法：{algorithm}")
    data = _encode(text, encoding, "文本")

    if hmac_key:
        key = _encode(hmac_key, encoding, "HMAC 密钥")
        digest = hmac.new(key, data, digest_name).hexdigest()
    else:
        digest = hashlib.new(digest_name, data).hexdigest()
    return digest.upper()


def verify_hash(
    text: str,
    expected: str,
    algorithm: str,
    encoding: str = "UTF-8",
    hmac_key: str = "",
) -> bool:
    """校验文本哈希是否与期望值一致（忽略大小写、空白与 0x 前缀）。"""
    cleaned = _normalize_digest(expected)
    if not cleaned:
        raise HashError("请输入期望哈希值")
    actual = calculate_hash(text, algorithm, encoding, hmac_key)
    return hmac.compare_digest(actual.lower(), cleaned)


def _encode(value: str, encoding: str, label: str) -> bytes:
    try:
        return value.encode(encoding)
    except (LookupError, UnicodeEncodeError) as exc:
        raise HashError(f"{label}无法使用 {encoding} 编码：{exc}") from exc


def _normalize_digest(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "".join(text.split())
