"""密码学工具的 Controller 层。"""

from typing import Optional

from base64_codec import Base64CodecError
from crc_service import CrcError
from model import Base64Model, CrcModel, SymmetricCryptoModel
from symmetric_crypto import CryptoError
from view import CryptoToolView


class AppController:
    """协调 Base64、现代对称加密、CRC Model 与 View。"""

    def __init__(
        self,
        base64_model: Optional[Base64Model] = None,
        crypto_model: Optional[SymmetricCryptoModel] = None,
        crc_model: Optional[CrcModel] = None,
        view: Optional[CryptoToolView] = None,
    ) -> None:
        self.base64_model = base64_model or Base64Model()
        self.crypto_model = crypto_model or SymmetricCryptoModel()
        self.crc_model = crc_model or CrcModel()
        self.view = view or CryptoToolView()
        self._initialize_view()
        self._connect_signals()

    def _initialize_view(self) -> None:
        self.view.set_supported_encodings(self.base64_model.supported_encodings)
        self.view.set_crypto_options(
            self.crypto_model.algorithms,
            self.crypto_model.key_modes,
            self.crypto_model.binary_encodings,
            self.crypto_model.text_encodings,
        )
        self.view.set_crc_options(
            self.crc_model.algorithms,
            self.crc_model.text_encodings,
        )

    def _connect_signals(self) -> None:
        self.view.encode_requested.connect(self.encode_content)
        self.view.decode_requested.connect(self.decode_content)
        self.view.swap_requested.connect(self.swap_content)
        self.view.copy_requested.connect(self.copy_output)
        self.view.clear_requested.connect(self.clear_content)
        self.view.theme_changed.connect(self.change_theme)

        self.view.crypto_encrypt_requested.connect(self.encrypt_content)
        self.view.crypto_decrypt_requested.connect(self.decrypt_content)
        self.view.crypto_generate_key_requested.connect(self.generate_crypto_key)
        self.view.crypto_copy_requested.connect(self.copy_crypto_output)
        self.view.crypto_clear_requested.connect(self.clear_crypto)

        self.view.crc_calculate_requested.connect(self.calculate_crc)
        self.view.crc_verify_requested.connect(self.verify_crc)
        self.view.crc_copy_requested.connect(self.copy_crc_output)
        self.view.crc_clear_requested.connect(self.clear_crc)

    def _sync_base64_options(self) -> bool:
        try:
            self.base64_model.configure(
                encoding=self.view.selected_encoding(),
                url_safe=self.view.is_url_safe(),
                fix_padding=self.view.should_fix_padding(),
            )
        except Base64CodecError as exc:
            self.view.show_error(str(exc))
            return False
        return True

    def _sync_crypto_options(self) -> None:
        self.crypto_model.configure(
            algorithm=self.view.crypto_algorithm(),
            key_mode=self.view.crypto_key_mode(),
            key_encoding=self.view.crypto_key_encoding(),
            output_encoding=self.view.crypto_output_encoding(),
            text_encoding=self.view.crypto_text_encoding(),
            aad=self.view.crypto_aad(),
        )

    def _sync_crc_options(self) -> None:
        self.crc_model.configure(
            algorithm=self.view.crc_algorithm(),
            encoding=self.view.crc_encoding(),
        )

    def encode_content(self) -> None:
        if not self._sync_base64_options():
            return
        try:
            result = self.base64_model.encode(self.view.input_text())
        except Base64CodecError as exc:
            self.view.show_error(str(exc))
            return
        self.view.set_output_text(result)
        self.view.show_success("编码完成")

    def decode_content(self) -> None:
        if not self._sync_base64_options():
            return
        try:
            result = self.base64_model.decode(self.view.input_text())
        except Base64CodecError as exc:
            self.view.show_error(str(exc))
            return
        self.view.set_output_text(result)
        self.view.show_success("解码完成")

    def swap_content(self) -> None:
        result = self.view.output_text()
        if not result:
            self.view.show_error("当前没有可转为输入的结果")
            return
        self.view.set_input_text(result)
        self.view.set_output_text("")
        self.view.focus_input()

    def copy_output(self) -> None:
        self._copy_result(self.view.output_text())

    def clear_content(self) -> None:
        self.view.clear_text()
        self.view.focus_input()

    def encrypt_content(self) -> None:
        self._sync_crypto_options()
        try:
            result = self.crypto_model.encrypt(
                self.view.crypto_input(), self.view.crypto_secret()
            )
        except CryptoError as exc:
            self.view.show_error(str(exc))
            return
        self.view.set_crypto_output(result)
        self.view.show_success("加密完成，随机 salt 和 nonce/IV 已写入 envelope")

    def decrypt_content(self) -> None:
        self._sync_crypto_options()
        try:
            result = self.crypto_model.decrypt(
                self.view.crypto_input(), self.view.crypto_secret()
            )
        except CryptoError as exc:
            self.view.show_error(str(exc))
            return
        self.view.set_crypto_output(result)
        self.view.show_success("解密完成")

    def generate_crypto_key(self) -> None:
        self._sync_crypto_options()
        try:
            key = self.crypto_model.generate_key()
        except CryptoError as exc:
            self.view.show_error(str(exc))
            return
        self.view.set_crypto_secret(key)
        self.view.show_success("已生成安全随机密钥")

    def copy_crypto_output(self) -> None:
        self._copy_result(self.view.crypto_output())

    def clear_crypto(self) -> None:
        self.view.clear_crypto()
        self.view.focus_crypto_input()

    def calculate_crc(self) -> None:
        self._sync_crc_options()
        try:
            result = self.crc_model.calculate(self.view.crc_input())
        except CrcError as exc:
            self.view.show_error(str(exc))
            return
        self.view.set_crc_output(result)
        self.view.show_success("CRC 计算完成")

    def verify_crc(self) -> None:
        self._sync_crc_options()
        try:
            result = self.crc_model.calculate(self.view.crc_input())
            matched = self.crc_model.verify(
                self.view.crc_input(), self.view.crc_expected()
            )
        except CrcError as exc:
            self.view.show_error(str(exc))
            return
        self.view.set_crc_output(result)
        if matched:
            self.view.show_success("CRC 校验一致")
        else:
            self.view.show_warning("CRC 校验不一致")

    def copy_crc_output(self) -> None:
        self._copy_result(self.view.crc_output())

    def clear_crc(self) -> None:
        self.view.clear_crc()

    def _copy_result(self, result: str) -> None:
        if not result:
            self.view.show_error("当前没有可复制的结果")
            return
        self.view.copy_to_clipboard(result)
        self.view.show_success("结果已复制到剪贴板")

    def change_theme(self, index: int) -> None:
        self.view.apply_theme(index)

    def show(self) -> None:
        self.view.show()


Base64Controller = AppController
