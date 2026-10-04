"""密码学工具的 Controller 层。"""

from typing import Optional

from app.models import (
    Base64Model,
    CrcModel,
    HashModel,
    PasswordModel,
    SettingsModel,
    SymmetricCryptoModel,
)
from app.services.base64_codec import Base64CodecError
from app.services.crc_service import CrcError
from app.services.hash_service import HashError
from app.services.password_service import PasswordError
from app.services.symmetric_crypto import CryptoError
from app.views import CryptoToolView


class AppController:
    """协调 Base64、对称加密、CRC、哈希、密码生成 Model 与 View。"""

    def __init__(
        self,
        base64_model: Optional[Base64Model] = None,
        crypto_model: Optional[SymmetricCryptoModel] = None,
        crc_model: Optional[CrcModel] = None,
        hash_model: Optional[HashModel] = None,
        password_model: Optional[PasswordModel] = None,
        settings_model: Optional[SettingsModel] = None,
        view: Optional[CryptoToolView] = None,
    ) -> None:
        self.base64_model = base64_model or Base64Model()
        self.crypto_model = crypto_model or SymmetricCryptoModel()
        self.crc_model = crc_model or CrcModel()
        self.hash_model = hash_model or HashModel()
        self.password_model = password_model or PasswordModel()
        self.settings_model = settings_model or SettingsModel()
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
        self.view.set_hash_options(
            self.hash_model.algorithms,
            self.hash_model.text_encodings,
        )
        self._initialize_settings()
        self._update_password_strength()

    def _initialize_settings(self) -> None:
        """把持久化设置恢复到界面并应用副作用。"""
        options = self.settings_model.options
        self.view.init_settings(
            theme=options.theme,
            theme_color=options.theme_color,
            always_on_top=options.always_on_top,
            default_page=options.default_page,
            page_names=self.settings_model.PAGE_NAMES,
            auto_copy=options.auto_copy,
        )
        self.view.apply_theme(options.theme)
        self.view.apply_theme_color(options.theme_color)
        self.view.set_always_on_top(options.always_on_top)
        self.view.switch_to_page(options.default_page)

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

        self.view.hash_calculate_requested.connect(self.calculate_hash)
        self.view.hash_verify_requested.connect(self.verify_hash)
        self.view.hash_copy_requested.connect(self.copy_hash_output)
        self.view.hash_clear_requested.connect(self.clear_hash)

        self.view.password_generate_requested.connect(self.generate_password)
        self.view.password_copy_requested.connect(self.copy_password_output)
        self.view.password_options_changed.connect(self.refresh_password_strength)

        self.view.theme_color_changed.connect(self.change_theme_color)
        self.view.always_on_top_changed.connect(self.change_always_on_top)
        self.view.default_page_changed.connect(self.change_default_page)
        self.view.auto_copy_changed.connect(self.change_auto_copy)
        self.view.settings_reset_requested.connect(self.reset_settings)

    # ---- Base64 ----

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

    def encode_content(self) -> None:
        if not self._sync_base64_options():
            return
        try:
            result = self.base64_model.encode(self.view.input_text())
        except Base64CodecError as exc:
            self.view.show_error(str(exc))
            return
        self.view.set_output_text(result)
        self.view.show_success(self._succeed("编码完成", result))

    def decode_content(self) -> None:
        if not self._sync_base64_options():
            return
        try:
            result = self.base64_model.decode(self.view.input_text())
        except Base64CodecError as exc:
            self.view.show_error(str(exc))
            return
        self.view.set_output_text(result)
        self.view.show_success(self._succeed("解码完成", result))

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

    # ---- 对称加密 ----

    def _sync_crypto_options(self) -> None:
        self.crypto_model.configure(
            algorithm=self.view.crypto_algorithm(),
            key_mode=self.view.crypto_key_mode(),
            key_encoding=self.view.crypto_key_encoding(),
            output_encoding=self.view.crypto_output_encoding(),
            text_encoding=self.view.crypto_text_encoding(),
            aad=self.view.crypto_aad(),
        )

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
        self.view.show_success(
            self._succeed("加密完成，随机 salt 和 nonce/IV 已写入 envelope", result)
        )

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
        self.view.show_success(self._succeed("解密完成", result))

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

    # ---- CRC ----

    def _sync_crc_options(self) -> None:
        self.crc_model.configure(
            algorithm=self.view.crc_algorithm(),
            encoding=self.view.crc_encoding(),
        )

    def calculate_crc(self) -> None:
        self._sync_crc_options()
        try:
            result = self.crc_model.calculate(self.view.crc_input())
        except CrcError as exc:
            self.view.show_error(str(exc))
            return
        self.view.set_crc_output(result)
        self.view.show_success(self._succeed("CRC 计算完成", result))

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

    # ---- 哈希 ----

    def _sync_hash_options(self) -> None:
        self.hash_model.configure(
            algorithm=self.view.hash_algorithm(),
            encoding=self.view.hash_encoding(),
            hmac_key=self.view.hash_hmac_key(),
        )

    def calculate_hash(self) -> None:
        self._sync_hash_options()
        try:
            result = self.hash_model.calculate(self.view.hash_input())
        except HashError as exc:
            self.view.show_error(str(exc))
            return
        self.view.set_hash_output(result)
        self.view.show_success(self._succeed("哈希计算完成", result))

    def verify_hash(self) -> None:
        self._sync_hash_options()
        try:
            result = self.hash_model.calculate(self.view.hash_input())
            matched = self.hash_model.verify(
                self.view.hash_input(), self.view.hash_expected()
            )
        except HashError as exc:
            self.view.show_error(str(exc))
            return
        self.view.set_hash_output(result)
        if matched:
            self.view.show_success("哈希校验一致")
        else:
            self.view.show_warning("哈希校验不一致")

    def copy_hash_output(self) -> None:
        self._copy_result(self.view.hash_output())

    def clear_hash(self) -> None:
        self.view.clear_hash()

    # ---- 密码生成 ----

    def _sync_password_options(self) -> None:
        self.password_model.configure(
            length=self.view.password_length(),
            use_upper=self.view.password_use_upper(),
            use_lower=self.view.password_use_lower(),
            use_digits=self.view.password_use_digits(),
            use_symbols=self.view.password_use_symbols(),
            exclude_ambiguous=self.view.password_exclude_ambiguous(),
        )

    def _update_password_strength(self) -> None:
        try:
            label, bits = self.password_model.strength()
        except PasswordError:
            self.view.set_password_strength("请至少选择一种字符集")
            return
        self.view.set_password_strength(f"强度：{label}（约 {bits} 位熵）")

    def generate_password(self) -> None:
        self._sync_password_options()
        try:
            password = self.password_model.generate()
        except PasswordError as exc:
            self.view.show_error(str(exc))
            return
        self.view.set_password_output(password)
        self._update_password_strength()
        self.view.show_success(self._succeed("已生成随机密码", password))

    def refresh_password_strength(self) -> None:
        self._sync_password_options()
        self._update_password_strength()

    def copy_password_output(self) -> None:
        self._copy_result(self.view.password_output())

    # ---- 设置 ----

    def change_theme(self, index: int) -> None:
        self.view.apply_theme(index)
        self.settings_model.configure(theme=index)

    def change_theme_color(self, color: str) -> None:
        self.view.apply_theme_color(color)
        self.view.set_theme_color_swatch(color)
        self.settings_model.configure(theme_color=color)

    def change_always_on_top(self, on_top: bool) -> None:
        self.view.set_always_on_top(on_top)
        self.settings_model.configure(always_on_top=on_top)

    def change_default_page(self, name: str) -> None:
        self.settings_model.configure(default_page=name)

    def change_auto_copy(self, enabled: bool) -> None:
        self.settings_model.configure(auto_copy=enabled)

    def reset_settings(self) -> None:
        options = self.settings_model.reset()
        self.view.init_settings(
            theme=options.theme,
            theme_color=options.theme_color,
            always_on_top=options.always_on_top,
            default_page=options.default_page,
            page_names=self.settings_model.PAGE_NAMES,
            auto_copy=options.auto_copy,
        )
        self.view.apply_theme(options.theme)
        self.view.apply_theme_color(options.theme_color)
        self.view.set_always_on_top(options.always_on_top)
        self.view.show_success("已恢复默认设置")

    # ---- 通用 ----

    def _succeed(self, message: str, result: str) -> str:
        """生成成功提示；开启自动复制时顺带复制结果。"""
        if self.settings_model.options.auto_copy and result:
            self.view.copy_to_clipboard(result)
            return f"{message}，结果已自动复制"
        return message

    def _copy_result(self, result: str) -> None:
        if not result:
            self.view.show_error("当前没有可复制的结果")
            return
        self.view.copy_to_clipboard(result)
        self.view.show_success("结果已复制到剪贴板")

    def show(self) -> None:
        self.view.showMaximized()
