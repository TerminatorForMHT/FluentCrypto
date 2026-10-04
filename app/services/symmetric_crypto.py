"""现代对称加密核心服务。"""

import base64
import binascii
import json
import os
from typing import Any, Dict, Final, Tuple

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


SUPPORTED_ALGORITHMS: Final = (
    "AES-256-GCM",
    "AES-192-GCM",
    "AES-128-GCM",
    "ChaCha20-Poly1305",
    "AES-256-CBC",
    "AES-192-CBC",
    "AES-128-CBC",
)
SUPPORTED_KEY_MODES: Final = ("密码", "原始密钥")
SUPPORTED_BINARY_ENCODINGS: Final = ("Base64", "Hex")
SUPPORTED_TEXT_ENCODINGS: Final = ("UTF-8", "GBK")
SCRYPT_N: Final = 16384
SCRYPT_R: Final = 8
SCRYPT_P: Final = 1


class CryptoError(ValueError):
    """对称加密操作失败。"""


def key_size_bytes(algorithm: str) -> int:
    """返回算法要求的密钥字节数。"""
    if algorithm == "ChaCha20-Poly1305":
        return 32
    try:
        bits = int(algorithm.split("-")[1])
    except (IndexError, ValueError) as exc:
        raise CryptoError(f"不支持的加密算法：{algorithm}") from exc
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise CryptoError(f"不支持的加密算法：{algorithm}")
    return bits // 8


def generate_raw_key(algorithm: str, binary_encoding: str = "Base64") -> str:
    """生成符合算法长度要求的安全随机密钥。"""
    return _encode_binary(os.urandom(key_size_bytes(algorithm)), binary_encoding)


def encrypt_text(
    text: str,
    secret: str,
    algorithm: str = "AES-256-GCM",
    key_mode: str = "密码",
    key_encoding: str = "Base64",
    output_encoding: str = "Base64",
    text_encoding: str = "UTF-8",
    aad_text: str = "",
) -> str:
    """加密文本并返回自描述 JSON envelope。"""
    _validate_algorithm(algorithm)
    _validate_text_encoding(text_encoding)
    _validate_binary_encoding(output_encoding)
    plaintext = _encode_text(text, text_encoding)
    aad = _encode_text(aad_text, text_encoding)
    salt = os.urandom(16) if key_mode == "密码" else b""
    key = _resolve_key(secret, algorithm, key_mode, key_encoding, salt)

    envelope: Dict[str, Any] = {
        "version": 1,
        "algorithm": algorithm,
        "key_bits": len(key) * 8,
        "key_mode": "password" if key_mode == "密码" else "raw",
        "encoding": text_encoding,
        "binary_encoding": output_encoding,
        "ciphertext": "",
    }
    if salt:
        envelope["kdf"] = {
            "name": "scrypt",
            "salt": _encode_binary(salt, output_encoding),
            "n": SCRYPT_N,
            "r": SCRYPT_R,
            "p": SCRYPT_P,
        }

    try:
        if algorithm.endswith("GCM"):
            nonce = os.urandom(12)
            encrypted = AESGCM(key).encrypt(nonce, plaintext, aad or None)
            envelope.update(
                nonce=_encode_binary(nonce, output_encoding),
                ciphertext=_encode_binary(encrypted[:-16], output_encoding),
                tag=_encode_binary(encrypted[-16:], output_encoding),
                aad=_encode_binary(aad, output_encoding),
            )
        elif algorithm == "ChaCha20-Poly1305":
            nonce = os.urandom(12)
            encrypted = ChaCha20Poly1305(key).encrypt(nonce, plaintext, aad or None)
            envelope.update(
                nonce=_encode_binary(nonce, output_encoding),
                ciphertext=_encode_binary(encrypted[:-16], output_encoding),
                tag=_encode_binary(encrypted[-16:], output_encoding),
                aad=_encode_binary(aad, output_encoding),
            )
        else:
            iv = os.urandom(16)
            padder = padding.PKCS7(128).padder()
            padded = padder.update(plaintext) + padder.finalize()
            encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
            ciphertext = encryptor.update(padded) + encryptor.finalize()
            envelope.update(
                iv=_encode_binary(iv, output_encoding),
                ciphertext=_encode_binary(ciphertext, output_encoding),
            )
    except (ValueError, TypeError) as exc:
        raise CryptoError(f"加密失败：{exc}") from exc

    return json.dumps(envelope, ensure_ascii=False, indent=2)


def decrypt_text(
    envelope_text: str,
    secret: str,
    key_encoding: str = "Base64",
) -> str:
    """解析 JSON envelope 并解密为文本。"""
    envelope = _parse_envelope(envelope_text)
    algorithm = _required_string(envelope, "algorithm")
    _validate_algorithm(algorithm)
    text_encoding = _required_string(envelope, "encoding")
    _validate_text_encoding(text_encoding)
    binary_encoding = _required_string(envelope, "binary_encoding")
    _validate_binary_encoding(binary_encoding)
    if envelope.get("key_bits") != key_size_bytes(algorithm) * 8:
        raise CryptoError("加密数据中的密钥长度与算法不匹配")
    key_mode = _required_string(envelope, "key_mode")

    if key_mode == "password":
        kdf = envelope.get("kdf")
        if not isinstance(kdf, dict) or kdf.get("name") != "scrypt":
            raise CryptoError("加密数据缺少有效的 Scrypt 参数")
        if (kdf.get("n"), kdf.get("r"), kdf.get("p")) != (
            SCRYPT_N,
            SCRYPT_R,
            SCRYPT_P,
        ):
            raise CryptoError("加密数据包含不受支持的 Scrypt 参数")
        salt = _decode_envelope_field(kdf, "salt", binary_encoding, 16)
        key = _resolve_key(secret, algorithm, "密码", key_encoding, salt)
    elif key_mode == "raw":
        key = _resolve_key(secret, algorithm, "原始密钥", key_encoding, b"")
    else:
        raise CryptoError("加密数据包含未知的密钥模式")

    ciphertext = _decode_envelope_field(envelope, "ciphertext", binary_encoding)
    try:
        if algorithm.endswith("GCM"):
            nonce = _decode_envelope_field(envelope, "nonce", binary_encoding, 12)
            tag = _decode_envelope_field(envelope, "tag", binary_encoding, 16)
            aad = _decode_optional_envelope_field(
                envelope, "aad", binary_encoding
            )
            plaintext = AESGCM(key).decrypt(nonce, ciphertext + tag, aad or None)
        elif algorithm == "ChaCha20-Poly1305":
            nonce = _decode_envelope_field(envelope, "nonce", binary_encoding, 12)
            tag = _decode_envelope_field(envelope, "tag", binary_encoding, 16)
            aad = _decode_optional_envelope_field(
                envelope, "aad", binary_encoding
            )
            plaintext = ChaCha20Poly1305(key).decrypt(
                nonce, ciphertext + tag, aad or None
            )
        else:
            iv = _decode_envelope_field(envelope, "iv", binary_encoding, 16)
            decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
            padded = decryptor.update(ciphertext) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded) + unpadder.finalize()
    except InvalidTag as exc:
        raise CryptoError("密码/密钥错误或密文已被篡改") from exc
    except ValueError as exc:
        if algorithm.endswith("CBC"):
            raise CryptoError("密码/密钥错误，或 CBC 密文/填充无效") from exc
        raise CryptoError(f"解密失败：{exc}") from exc

    try:
        return plaintext.decode(text_encoding)
    except UnicodeDecodeError as exc:
        raise CryptoError(
            f"解密结果不是有效的 {text_encoding} 文本，密钥可能不正确"
        ) from exc


def _resolve_key(
    secret: str,
    algorithm: str,
    key_mode: str,
    key_encoding: str,
    salt: bytes,
) -> bytes:
    length = key_size_bytes(algorithm)
    if not secret:
        raise CryptoError("密码或密钥不能为空")
    if key_mode == "密码":
        try:
            return Scrypt(
                salt=salt,
                length=length,
                n=SCRYPT_N,
                r=SCRYPT_R,
                p=SCRYPT_P,
            ).derive(secret.encode("UTF-8"))
        except (TypeError, ValueError) as exc:
            raise CryptoError(f"密钥派生失败：{exc}") from exc
    if key_mode != "原始密钥":
        raise CryptoError(f"不支持的密钥模式：{key_mode}")
    key = _decode_binary(secret, key_encoding)
    if len(key) != length:
        raise CryptoError(f"{algorithm} 需要 {length} 字节密钥，当前为 {len(key)} 字节")
    return key


def _parse_envelope(value: str) -> Dict[str, Any]:
    try:
        envelope = json.loads(value)
    except (json.JSONDecodeError, TypeError) as exc:
        raise CryptoError("输入不是有效的加密 JSON envelope") from exc
    if not isinstance(envelope, dict) or envelope.get("version") != 1:
        raise CryptoError("不支持的加密数据格式或版本")
    return envelope


def _required_string(mapping: Dict[str, Any], field: str) -> str:
    value = mapping.get(field)
    if not isinstance(value, str) or not value:
        raise CryptoError(f"加密数据缺少字段：{field}")
    return value


def _decode_envelope_field(
    mapping: Dict[str, Any],
    field: str,
    encoding: str,
    expected_length: int = -1,
) -> bytes:
    value = mapping.get(field)
    if not isinstance(value, str):
        raise CryptoError(f"加密数据缺少字段：{field}")
    try:
        result = _decode_binary_value(value, encoding)
    except CryptoError as exc:
        raise CryptoError(f"字段 {field} 不是有效的 {encoding}") from exc
    if expected_length >= 0 and len(result) != expected_length:
        raise CryptoError(f"字段 {field} 长度无效")
    return result


def _decode_optional_envelope_field(
    mapping: Dict[str, Any], field: str, encoding: str
) -> bytes:
    value = mapping.get(field, "")
    if not isinstance(value, str):
        raise CryptoError(f"字段 {field} 格式无效")
    if not value:
        return b""
    return _decode_envelope_field(mapping, field, encoding)


def _encode_text(value: str, encoding: str) -> bytes:
    try:
        return value.encode(encoding)
    except UnicodeEncodeError as exc:
        raise CryptoError(f"文本无法使用 {encoding} 编码：{exc}") from exc


def _decode_binary(value: str, encoding: str) -> bytes:
    try:
        return _decode_binary_value(value, encoding)
    except CryptoError as exc:
        raise CryptoError(f"原始密钥不是有效的 {encoding} 数据") from exc


def _decode_binary_value(value: str, encoding: str) -> bytes:
    compact = "".join(value.split())
    try:
        if encoding == "Hex":
            return bytes.fromhex(compact)
        if encoding == "Base64":
            return base64.b64decode(compact, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise CryptoError(f"数据不是有效的 {encoding}") from exc
    raise CryptoError(f"不支持的二进制编码：{encoding}")


def _encode_binary(value: bytes, encoding: str) -> str:
    if encoding == "Hex":
        return value.hex().upper()
    if encoding == "Base64":
        return _b64(value)
    raise CryptoError(f"不支持的二进制编码：{encoding}")


def _b64(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _validate_algorithm(algorithm: str) -> None:
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise CryptoError(f"不支持的加密算法：{algorithm}")


def _validate_text_encoding(encoding: str) -> None:
    if encoding not in SUPPORTED_TEXT_ENCODINGS:
        raise CryptoError(f"不支持的文本编码：{encoding}")


def _validate_binary_encoding(encoding: str) -> None:
    if encoding not in SUPPORTED_BINARY_ENCODINGS:
        raise CryptoError(f"不支持的二进制编码：{encoding}")
