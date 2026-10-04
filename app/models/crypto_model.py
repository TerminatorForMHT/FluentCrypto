"""现代对称加密模型。"""

from dataclasses import dataclass
from typing import Tuple

from app.services.symmetric_crypto import (
    SUPPORTED_ALGORITHMS,
    SUPPORTED_BINARY_ENCODINGS,
    SUPPORTED_KEY_MODES,
    SUPPORTED_TEXT_ENCODINGS,
    decrypt_text,
    encrypt_text,
    generate_raw_key,
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
