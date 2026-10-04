"""主窗口：组装各功能页面并向 Controller 暴露统一接口。"""

from typing import Callable, Iterable

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QShortcut
from qfluentwidgets import (
    FluentIcon as FIF,
    FluentWindow,
    InfoBar,
    InfoBarPosition,
    NavigationItemPosition,
    Theme,
    setTheme,
    setThemeColor,
)

from app.views.pages.base64_page import Base64Page
from app.views.pages.crc_page import CrcPage
from app.views.pages.crypto_page import CryptoPage
from app.views.pages.hash_page import HashPage
from app.views.pages.password_page import PasswordPage
from app.views.pages.settings_page import SettingsPage


class CryptoToolView(FluentWindow):
    """仅负责界面展示、表单读取和用户事件发送。"""

    encode_requested = pyqtSignal()
    decode_requested = pyqtSignal()
    swap_requested = pyqtSignal()
    copy_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    theme_changed = pyqtSignal(int)
    theme_color_changed = pyqtSignal(str)
    always_on_top_changed = pyqtSignal(bool)
    default_page_changed = pyqtSignal(str)
    auto_copy_changed = pyqtSignal(bool)
    settings_reset_requested = pyqtSignal()

    crypto_encrypt_requested = pyqtSignal()
    crypto_decrypt_requested = pyqtSignal()
    crypto_generate_key_requested = pyqtSignal()
    crypto_copy_requested = pyqtSignal()
    crypto_clear_requested = pyqtSignal()

    crc_calculate_requested = pyqtSignal()
    crc_verify_requested = pyqtSignal()
    crc_copy_requested = pyqtSignal()
    crc_clear_requested = pyqtSignal()

    hash_calculate_requested = pyqtSignal()
    hash_verify_requested = pyqtSignal()
    hash_copy_requested = pyqtSignal()
    hash_clear_requested = pyqtSignal()

    password_generate_requested = pyqtSignal()
    password_copy_requested = pyqtSignal()
    password_options_changed = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("密码学编码校验工具")
        self.resize(1080, 820)
        self.setMinimumSize(820, 680)

        self._build_ui()
        self.navigationInterface.setExpandWidth(190)
        self._connect_page_signals()
        self._register_shortcuts()

    def _build_ui(self) -> None:
        self.base64_page = Base64Page(self)
        self.crypto_page = CryptoPage(self)
        self.crc_page = CrcPage(self)
        self.hash_page = HashPage(self)
        self.password_page = PasswordPage(self)
        self.settings_page = SettingsPage(self)

        self.addSubInterface(
            self.base64_page,
            FIF.CODE,
            "Base64",
            isTransparent=True,
        )
        self.addSubInterface(
            self.crypto_page,
            FIF.FINGERPRINT,
            "对称加密",
            isTransparent=True,
        )
        self.addSubInterface(
            self.crc_page,
            FIF.CALORIES,
            "CRC 校验",
            isTransparent=True,
        )
        self.addSubInterface(
            self.hash_page,
            FIF.TAG,
            "哈希工具",
            isTransparent=True,
        )
        self.addSubInterface(
            self.password_page,
            FIF.PIN,
            "密码生成",
            isTransparent=True,
        )
        self.addSubInterface(
            self.settings_page,
            FIF.SETTING,
            "设置",
            position=NavigationItemPosition.BOTTOM,
            isTransparent=True,
        )

        # 与 SettingsModel.PAGE_NAMES 的顺序与名称保持一致
        self._pages = {
            "Base64": self.base64_page,
            "对称加密": self.crypto_page,
            "CRC 校验": self.crc_page,
            "哈希工具": self.hash_page,
            "密码生成": self.password_page,
        }

    def _connect_page_signals(self) -> None:
        page = self.base64_page
        page.encode_requested.connect(self.encode_requested.emit)
        page.decode_requested.connect(self.decode_requested.emit)
        page.swap_requested.connect(self.swap_requested.emit)
        page.copy_requested.connect(self.copy_requested.emit)
        page.clear_requested.connect(self.clear_requested.emit)

        page = self.crypto_page
        page.encrypt_requested.connect(self.crypto_encrypt_requested.emit)
        page.decrypt_requested.connect(self.crypto_decrypt_requested.emit)
        page.generate_key_requested.connect(self.crypto_generate_key_requested.emit)
        page.copy_requested.connect(self.crypto_copy_requested.emit)
        page.clear_requested.connect(self.crypto_clear_requested.emit)

        page = self.crc_page
        page.calculate_requested.connect(self.crc_calculate_requested.emit)
        page.verify_requested.connect(self.crc_verify_requested.emit)
        page.copy_requested.connect(self.crc_copy_requested.emit)
        page.clear_requested.connect(self.crc_clear_requested.emit)

        page = self.hash_page
        page.calculate_requested.connect(self.hash_calculate_requested.emit)
        page.verify_requested.connect(self.hash_verify_requested.emit)
        page.copy_requested.connect(self.hash_copy_requested.emit)
        page.clear_requested.connect(self.hash_clear_requested.emit)

        page = self.password_page
        page.generate_requested.connect(self.password_generate_requested.emit)
        page.copy_requested.connect(self.password_copy_requested.emit)
        page.options_changed.connect(self.password_options_changed.emit)

        page = self.settings_page
        page.theme_changed.connect(self.theme_changed.emit)
        page.theme_color_changed.connect(self.theme_color_changed.emit)
        page.always_on_top_changed.connect(self.always_on_top_changed.emit)
        page.default_page_changed.connect(self.default_page_changed.emit)
        page.auto_copy_changed.connect(self.auto_copy_changed.emit)
        page.reset_requested.connect(self.settings_reset_requested.emit)

    def _register_shortcuts(self) -> None:
        self._add_shortcut("Ctrl+Return", self.encode_requested.emit)
        self._add_shortcut("Ctrl+Shift+Return", self.decode_requested.emit)
        self._add_shortcut("Ctrl+L", self.clear_requested.emit)

    def _add_shortcut(self, sequence: str, callback: Callable[[], None]) -> None:
        shortcut = QShortcut(QKeySequence(sequence), self)
        shortcut.activated.connect(callback)

    # ---- Base64 页接口 ----

    def set_supported_encodings(self, encodings: Iterable[str]) -> None:
        self.base64_page.set_supported_encodings(encodings)

    def input_text(self) -> str:
        return self.base64_page.input_text()

    def output_text(self) -> str:
        return self.base64_page.output_text()

    def selected_encoding(self) -> str:
        return self.base64_page.selected_encoding()

    def is_url_safe(self) -> bool:
        return self.base64_page.is_url_safe()

    def should_fix_padding(self) -> bool:
        return self.base64_page.should_fix_padding()

    def set_input_text(self, value: str) -> None:
        self.base64_page.set_input_text(value)

    def set_output_text(self, value: str) -> None:
        self.base64_page.set_output_text(value)

    def clear_text(self) -> None:
        self.base64_page.clear_text()

    def focus_input(self) -> None:
        self.base64_page.focus_input()

    # ---- 对称加密页接口 ----

    def set_crypto_options(
        self,
        algorithms: Iterable[str],
        key_modes: Iterable[str],
        binary_encodings: Iterable[str],
        text_encodings: Iterable[str],
    ) -> None:
        self.crypto_page.set_options(
            algorithms, key_modes, binary_encodings, text_encodings
        )

    def crypto_algorithm(self) -> str:
        return self.crypto_page.algorithm()

    def crypto_key_mode(self) -> str:
        return self.crypto_page.key_mode()

    def crypto_key_encoding(self) -> str:
        return self.crypto_page.key_encoding()

    def crypto_output_encoding(self) -> str:
        return self.crypto_page.output_encoding()

    def crypto_text_encoding(self) -> str:
        return self.crypto_page.text_encoding()

    def crypto_secret(self) -> str:
        return self.crypto_page.secret()

    def crypto_aad(self) -> str:
        return self.crypto_page.aad()

    def crypto_input(self) -> str:
        return self.crypto_page.input_text()

    def crypto_output(self) -> str:
        return self.crypto_page.output_text()

    def set_crypto_secret(self, value: str) -> None:
        self.crypto_page.set_secret(value)

    def set_crypto_output(self, value: str) -> None:
        self.crypto_page.set_output_text(value)

    def clear_crypto(self) -> None:
        self.crypto_page.clear()

    def focus_crypto_input(self) -> None:
        self.crypto_page.focus_input()

    # ---- CRC 页接口 ----

    def set_crc_options(
        self, algorithms: Iterable[str], text_encodings: Iterable[str]
    ) -> None:
        self.crc_page.set_options(algorithms, text_encodings)

    def crc_algorithm(self) -> str:
        return self.crc_page.algorithm()

    def crc_encoding(self) -> str:
        return self.crc_page.encoding()

    def crc_input(self) -> str:
        return self.crc_page.input_text()

    def crc_expected(self) -> str:
        return self.crc_page.expected()

    def crc_output(self) -> str:
        return self.crc_page.output_text()

    def set_crc_output(self, value: str) -> None:
        self.crc_page.set_output_text(value)

    def clear_crc(self) -> None:
        self.crc_page.clear()

    # ---- 哈希页接口 ----

    def set_hash_options(
        self, algorithms: Iterable[str], text_encodings: Iterable[str]
    ) -> None:
        self.hash_page.set_options(algorithms, text_encodings)

    def hash_algorithm(self) -> str:
        return self.hash_page.algorithm()

    def hash_encoding(self) -> str:
        return self.hash_page.encoding()

    def hash_hmac_key(self) -> str:
        return self.hash_page.hmac_key()

    def hash_input(self) -> str:
        return self.hash_page.input_text()

    def hash_expected(self) -> str:
        return self.hash_page.expected()

    def hash_output(self) -> str:
        return self.hash_page.output_text()

    def set_hash_output(self, value: str) -> None:
        self.hash_page.set_output_text(value)

    def clear_hash(self) -> None:
        self.hash_page.clear()

    # ---- 密码生成页接口 ----

    def password_length(self) -> int:
        return self.password_page.length()

    def password_use_upper(self) -> bool:
        return self.password_page.use_upper()

    def password_use_lower(self) -> bool:
        return self.password_page.use_lower()

    def password_use_digits(self) -> bool:
        return self.password_page.use_digits()

    def password_use_symbols(self) -> bool:
        return self.password_page.use_symbols()

    def password_exclude_ambiguous(self) -> bool:
        return self.password_page.exclude_ambiguous()

    def password_output(self) -> str:
        return self.password_page.password()

    def set_password_output(self, value: str) -> None:
        self.password_page.set_password(value)

    def set_password_strength(self, text: str) -> None:
        self.password_page.set_strength(text)

    # ---- 设置页接口 ----

    def init_settings(
        self,
        theme: int,
        theme_color: str,
        always_on_top: bool,
        default_page: str,
        page_names: Iterable[str],
        auto_copy: bool,
    ) -> None:
        self.settings_page.init_settings(
            theme, theme_color, always_on_top, default_page, page_names, auto_copy
        )

    def set_theme_color_swatch(self, color: str) -> None:
        self.settings_page.set_theme_color(color)

    def apply_theme_color(self, color: str) -> None:
        setThemeColor(color)

    def set_always_on_top(self, on_top: bool) -> None:
        self.setWindowFlag(Qt.WindowStaysOnTopHint, on_top)
        if self.isVisible():
            self.show()

    def switch_to_page(self, name: str) -> None:
        page = self._pages.get(name)
        if page is not None:
            self.switchTo(page)

    # ---- 通用接口 ----

    def copy_to_clipboard(self, value: str) -> None:
        QApplication.clipboard().setText(value)

    def apply_theme(self, index: int) -> None:
        themes = (Theme.AUTO, Theme.LIGHT, Theme.DARK)
        if 0 <= index < len(themes):
            setTheme(themes[index])

    def show_success(self, message: str) -> None:
        InfoBar.success(
            title="成功",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=1800,
            parent=self,
        )

    def show_error(self, message: str) -> None:
        InfoBar.error(
            title="操作失败",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3500,
            parent=self,
        )

    def show_warning(self, message: str) -> None:
        InfoBar.warning(
            title="校验结果",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self,
        )
