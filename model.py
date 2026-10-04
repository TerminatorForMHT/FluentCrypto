"""Base64 应用的 Model 层。"""

from dataclasses import dataclass
from typing import Tuple

from base64_codec import (
    Base64CodecError,
    SUPPORTED_ENCODINGS,
    decode_text,
    encode_text,
)
from crc_service import CRC_ALGORITHMS, calculate_crc, format_crc, verify_crc
from symmetric_crypto import (
    SUPPORTED_ALGORITHMS,
    SUPPORTED_BINARY_ENCODINGS,
    SUPPORTED_KEY_MODES,
    SUPPORTED_TEXT_ENCODINGS,
    decrypt_text,
    encrypt_text,
    generate_raw_key,
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


@dataclass(frozen=True)
class SymmetricCryptoOptions:
    """现代对称加密选项。"""

    algorithm: str = "AES-256-GCM"
    key_mode: str = "密码"
    key_encoding: str = "Base64"
    output_encoding: str = "Base64"
    text_encoding: str = "UTF-8"
    aad: str = ""


class SymmetricCryptoModel:
    """维护对称加密状态并调用加密服务。"""

    def __init__(self) -> None:
        self._options = SymmetricCryptoOptions()

    @property
    def algorithms(self) -> Tuple[str, ...]:
        return SUPPORTED_ALGORITHMS

    @property
    def key_modes(self) -> Tuple[str, ...]:
        return SUPPORTED_KEY_MODES

    @property
    def binary_encodings(self) -> Tuple[str, ...]:
        return SUPPORTED_BINARY_ENCODINGS

    @property
    def text_encodings(self) -> Tuple[str, ...]:
        return SUPPORTED_TEXT_ENCODINGS

    @property
    def options(self) -> SymmetricCryptoOptions:
        return self._options

    def configure(
        self,
        algorithm: str,
        key_mode: str,
        key_encoding: str,
        output_encoding: str,
        text_encoding: str,
        aad: str,
    ) -> None:
        self._options = SymmetricCryptoOptions(
            algorithm, key_mode, key_encoding, output_encoding, text_encoding, aad
        )

    def encrypt(self, text: str, secret: str) -> str:
        return encrypt_text(
            text,
            secret,
            algorithm=self._options.algorithm,
            key_mode=self._options.key_mode,
            key_encoding=self._options.key_encoding,
            output_encoding=self._options.output_encoding,
            text_encoding=self._options.text_encoding,
            aad_text=self._options.aad,
        )

    def decrypt(self, envelope: str, secret: str) -> str:
        return decrypt_text(
            envelope,
            secret,
            key_encoding=self._options.key_encoding,
        )

    def generate_key(self) -> str:
        return generate_raw_key(
            self._options.algorithm,
            self._options.key_encoding,
        )


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
