"""密码学工具的 QFluentWidgets View 层。"""

from typing import Callable, Iterable

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QShortcut,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    CardWidget,
    CheckBox,
    ComboBox,
    FluentIcon as FIF,
    FluentWindow,
    InfoBar,
    InfoBarPosition,
    LineEdit,
    NavigationItemPosition,
    PasswordLineEdit,
    PrimaryPushButton,
    PushButton,
    ScrollArea,
    StrongBodyLabel,
    SubtitleLabel,
    TextEdit,
    Theme,
    setTheme,
)


class CryptoToolView(FluentWindow):
    """仅负责界面展示、表单读取和用户事件发送。"""

    encode_requested = pyqtSignal()
    decode_requested = pyqtSignal()
    swap_requested = pyqtSignal()
    copy_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    theme_changed = pyqtSignal(int)

    crypto_encrypt_requested = pyqtSignal()
    crypto_decrypt_requested = pyqtSignal()
    crypto_generate_key_requested = pyqtSignal()
    crypto_copy_requested = pyqtSignal()
    crypto_clear_requested = pyqtSignal()

    crc_calculate_requested = pyqtSignal()
    crc_verify_requested = pyqtSignal()
    crc_copy_requested = pyqtSignal()
    crc_clear_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("密码学编码校验工具")
        self.resize(1080, 820)
        self.setMinimumSize(820, 680)

        self._create_controls()
        self._build_ui()
        self.navigationInterface.setExpandWidth(190)
        self._connect_view_signals()
        self._register_shortcuts()
        self._update_crypto_fields()

    def _create_controls(self) -> None:
        self.input_edit = TextEdit(self)
        self.output_edit = TextEdit(self)
        self.encoding_combo = ComboBox(self)
        self.theme_combo = ComboBox(self)
        self.url_safe_check = CheckBox("URL-safe", self)
        self.fix_padding_check = CheckBox("解码时自动补齐 padding", self)
        self.input_count_label = CaptionLabel("0 个字符", self)
        self.output_count_label = CaptionLabel("0 个字符", self)

        self.crypto_algorithm_combo = ComboBox(self)
        self.crypto_key_mode_combo = ComboBox(self)
        self.crypto_key_encoding_combo = ComboBox(self)
        self.crypto_output_encoding_combo = ComboBox(self)
        self.crypto_text_encoding_combo = ComboBox(self)
        self.crypto_secret_edit = PasswordLineEdit(self)
        self.crypto_secret_edit.setPlaceholderText("请输入密码或原始密钥")
        self.crypto_aad_edit = LineEdit(self)
        self.crypto_aad_edit.setPlaceholderText("可选的附加认证数据")
        self.crypto_input_edit = TextEdit(self)
        self.crypto_output_edit = TextEdit(self)
        self.crypto_warning_label = CaptionLabel("", self)
        self.crypto_key_encoding_label = StrongBodyLabel("密钥格式", self)
        self.crypto_aad_label = StrongBodyLabel("AAD", self)
        self.crypto_generate_button = PushButton(FIF.ADD, "生成密钥", self)

        self.crc_algorithm_combo = ComboBox(self)
        self.crc_encoding_combo = ComboBox(self)
        self.crc_expected_edit = LineEdit(self)
        self.crc_expected_edit.setPlaceholderText("例如 0xCBF43926 或十进制值")
        self.crc_input_edit = TextEdit(self)
        self.crc_output_edit = TextEdit(self)
        self.crc_output_edit.setReadOnly(True)

    def _build_ui(self) -> None:
        self.theme_combo.addItems(["跟随系统", "浅色", "深色"])
        self.base64_page = self._create_base64_page()
        self.crypto_page = self._create_crypto_page()
        self.crc_page = self._create_crc_page()
        self.settings_page = self._create_settings_page()

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
            self.settings_page,
            FIF.SETTING,
            "设置",
            position=NavigationItemPosition.BOTTOM,
            isTransparent=True,
        )

    def _create_page(self, object_name: str) -> tuple:
        scroll = ScrollArea(self)
        scroll.setObjectName(object_name)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        content = QWidget()
        content.setObjectName(f"{object_name}Content")
        content.setStyleSheet(
            f"QWidget#{object_name}Content {{ background: transparent; }}"
        )
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)
        scroll.setWidget(content)
        return scroll, layout

    def _create_base64_page(self) -> ScrollArea:
        page, layout = self._create_page("base64Page")
        layout.addWidget(SubtitleLabel("Base64 编码解码", self))
        layout.addWidget(
            BodyLabel("快速完成文本的 Base64 编码与解码，所有数据仅在本地处理。", self)
        )
        layout.addWidget(self._create_base64_settings_card())
        layout.addLayout(
            self._create_dual_editor_layout(
                self.input_edit,
                self.output_edit,
                "请输入待编码文本或 Base64 内容",
                "处理结果将显示在这里",
                self.input_count_label,
                self.output_count_label,
            ),
            1,
        )

        actions = QHBoxLayout()
        buttons = (
            PrimaryPushButton(FIF.RIGHT_ARROW, "编码", self),
            PrimaryPushButton(FIF.DOWNLOAD, "解码", self),
            PushButton(FIF.SYNC, "结果转为输入", self),
            PushButton(FIF.COPY, "复制结果", self),
            PushButton(FIF.DELETE, "清空", self),
        )
        signals = (
            self.encode_requested,
            self.decode_requested,
            self.swap_requested,
            self.copy_requested,
            self.clear_requested,
        )
        self._add_action_buttons(actions, buttons, signals)
        layout.addLayout(actions)
        return page

    def _create_base64_settings_card(self) -> CardWidget:
        card = CardWidget(self)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(12)
        layout.addWidget(StrongBodyLabel("字符编码", self))
        layout.addWidget(self.encoding_combo)
        self.fix_padding_check.setChecked(True)
        layout.addWidget(self.url_safe_check)
        layout.addWidget(self.fix_padding_check)
        layout.addStretch(1)
        return card

    def _create_settings_page(self) -> ScrollArea:
        page, layout = self._create_page("settingsPage")
        layout.addWidget(SubtitleLabel("设置", self))
        layout.addWidget(BodyLabel("调整应用的外观与显示选项。", self))

        card = CardWidget(self)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(18, 14, 18, 14)
        card_layout.addWidget(StrongBodyLabel("应用主题", self))
        card_layout.addStretch(1)
        card_layout.addWidget(self.theme_combo)
        layout.addWidget(card)
        layout.addStretch(1)
        return page

    def _create_crypto_page(self) -> ScrollArea:
        page, layout = self._create_page("cryptoPage")
        layout.addWidget(SubtitleLabel("现代对称加密", self))
        layout.addWidget(
            BodyLabel("使用现代对称算法加密文本；输出为不含密钥的 JSON envelope。", self)
        )
        layout.addWidget(self._create_crypto_settings_card())

        self.crypto_input_edit.setPlaceholderText("加密时输入明文，解密时输入 JSON envelope")
        self.crypto_output_edit.setPlaceholderText("加密或解密结果")
        self.crypto_input_edit.setAcceptRichText(False)
        self.crypto_output_edit.setAcceptRichText(False)
        layout.addLayout(
            self._create_dual_editor_layout(
                self.crypto_input_edit,
                self.crypto_output_edit,
                "加密时输入明文，解密时输入 JSON envelope",
                "加密或解密结果",
            ),
            1,
        )

        actions = QHBoxLayout()
        buttons = (
            PrimaryPushButton(FIF.FINGERPRINT, "加密", self),
            PrimaryPushButton(FIF.CERTIFICATE, "解密", self),
            PushButton(FIF.COPY, "复制结果", self),
            PushButton(FIF.DELETE, "清空", self),
        )
        signals = (
            self.crypto_encrypt_requested,
            self.crypto_decrypt_requested,
            self.crypto_copy_requested,
            self.crypto_clear_requested,
        )
        self._add_action_buttons(actions, buttons, signals)
        layout.addLayout(actions)
        return page

    def _create_crypto_settings_card(self) -> CardWidget:
        card = CardWidget(self)
        grid = QGridLayout(card)
        grid.setContentsMargins(18, 14, 18, 14)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        grid.addWidget(StrongBodyLabel("算法", self), 0, 0)
        grid.addWidget(self.crypto_algorithm_combo, 0, 1)
        grid.addWidget(StrongBodyLabel("文本编码", self), 0, 2)
        grid.addWidget(self.crypto_text_encoding_combo, 0, 3)
        grid.addWidget(StrongBodyLabel("密文格式", self), 0, 4)
        grid.addWidget(self.crypto_output_encoding_combo, 0, 5)
        grid.addWidget(StrongBodyLabel("密钥模式", self), 1, 0)
        grid.addWidget(self.crypto_key_mode_combo, 1, 1)
        grid.addWidget(self.crypto_key_encoding_label, 1, 2)
        grid.addWidget(self.crypto_key_encoding_combo, 1, 3)
        grid.addWidget(StrongBodyLabel("密码 / 密钥", self), 2, 0)
        grid.addWidget(self.crypto_secret_edit, 2, 1, 1, 4)
        grid.addWidget(self.crypto_generate_button, 2, 5)
        grid.addWidget(self.crypto_aad_label, 3, 0)
        grid.addWidget(self.crypto_aad_edit, 3, 1, 1, 5)
        grid.addWidget(self.crypto_warning_label, 4, 0, 1, 6)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        grid.setColumnStretch(5, 1)
        return card

    def _create_crc_page(self) -> ScrollArea:
        page, layout = self._create_page("crcPage")
        layout.addWidget(SubtitleLabel("CRC 校验", self))
        layout.addWidget(BodyLabel("计算或验证常见 CRC 校验值；CRC 不属于加密算法。", self))

        settings = CardWidget(self)
        grid = QGridLayout(settings)
        grid.setContentsMargins(18, 14, 18, 14)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)
        grid.addWidget(StrongBodyLabel("CRC 算法", self), 0, 0)
        grid.addWidget(self.crc_algorithm_combo, 0, 1)
        grid.addWidget(StrongBodyLabel("文本编码", self), 0, 2)
        grid.addWidget(self.crc_encoding_combo, 0, 3)
        grid.addWidget(StrongBodyLabel("期望 CRC", self), 1, 0)
        grid.addWidget(self.crc_expected_edit, 1, 1, 1, 3)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        layout.addWidget(settings)

        layout.addLayout(
            self._create_dual_editor_layout(
                self.crc_input_edit,
                self.crc_output_edit,
                "请输入待校验文本",
                "CRC 结果",
            ),
            1,
        )

        actions = QHBoxLayout()
        buttons = (
            PrimaryPushButton(FIF.CALORIES, "计算", self),
            PrimaryPushButton(FIF.ACCEPT, "验证", self),
            PushButton(FIF.COPY, "复制结果", self),
            PushButton(FIF.DELETE, "清空", self),
        )
        signals = (
            self.crc_calculate_requested,
            self.crc_verify_requested,
            self.crc_copy_requested,
            self.crc_clear_requested,
        )
        self._add_action_buttons(actions, buttons, signals)
        layout.addLayout(actions)
        return page

    def _create_dual_editor_layout(
        self,
        input_editor: TextEdit,
        output_editor: TextEdit,
        input_placeholder: str,
        output_placeholder: str,
        input_count: CaptionLabel = None,
        output_count: CaptionLabel = None,
    ) -> QGridLayout:
        layout = QGridLayout()
        layout.setHorizontalSpacing(16)
        layout.addWidget(
            self._create_editor_card("输入", input_editor, input_placeholder, input_count),
            0,
            0,
        )
        layout.addWidget(
            self._create_editor_card("输出", output_editor, output_placeholder, output_count),
            0,
            1,
        )
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        return layout

    def _create_editor_card(
        self,
        title: str,
        editor: TextEdit,
        placeholder: str,
        count_label: CaptionLabel = None,
    ) -> CardWidget:
        card = CardWidget(self)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 16)
        header = QHBoxLayout()
        header.addWidget(StrongBodyLabel(title, self))
        header.addStretch(1)
        if count_label is not None:
            header.addWidget(count_label)
        layout.addLayout(header)
        editor.setPlaceholderText(placeholder)
        editor.setAcceptRichText(False)
        layout.addWidget(editor, 1)
        return card

    def _add_action_buttons(self, layout, buttons, signals) -> None:
        layout.addStretch(1)
        for button, signal in zip(buttons, signals):
            button.clicked.connect(signal.emit)
            layout.addWidget(button)
        layout.addStretch(1)

    def _connect_view_signals(self) -> None:
        self.input_edit.textChanged.connect(self._update_base64_counts)
        self.output_edit.textChanged.connect(self._update_base64_counts)
        self.theme_combo.currentIndexChanged.connect(self.theme_changed.emit)
        self.crypto_algorithm_combo.currentIndexChanged.connect(
            self._update_crypto_fields
        )
        self.crypto_key_mode_combo.currentIndexChanged.connect(
            self._update_crypto_fields
        )
        self.crypto_generate_button.clicked.connect(
            self.crypto_generate_key_requested.emit
        )

    def _register_shortcuts(self) -> None:
        self._add_shortcut("Ctrl+Return", self.encode_requested.emit)
        self._add_shortcut("Ctrl+Shift+Return", self.decode_requested.emit)
        self._add_shortcut("Ctrl+L", self.clear_requested.emit)

    def _add_shortcut(self, sequence: str, callback: Callable[[], None]) -> None:
        shortcut = QShortcut(QKeySequence(sequence), self)
        shortcut.activated.connect(callback)

    def set_supported_encodings(self, encodings: Iterable[str]) -> None:
        self._set_combo_items(self.encoding_combo, encodings)

    def set_crypto_options(
        self,
        algorithms: Iterable[str],
        key_modes: Iterable[str],
        binary_encodings: Iterable[str],
        text_encodings: Iterable[str],
    ) -> None:
        self._set_combo_items(self.crypto_algorithm_combo, algorithms)
        self._set_combo_items(self.crypto_key_mode_combo, key_modes)
        self._set_combo_items(self.crypto_key_encoding_combo, binary_encodings)
        self._set_combo_items(self.crypto_output_encoding_combo, binary_encodings)
        self._set_combo_items(self.crypto_text_encoding_combo, text_encodings)
        self._update_crypto_fields()

    def set_crc_options(
        self, algorithms: Iterable[str], text_encodings: Iterable[str]
    ) -> None:
        self._set_combo_items(self.crc_algorithm_combo, algorithms)
        self._set_combo_items(self.crc_encoding_combo, text_encodings)
        index = self.crc_algorithm_combo.findText("CRC-32/ISO-HDLC")
        if index >= 0:
            self.crc_algorithm_combo.setCurrentIndex(index)

    @staticmethod
    def _set_combo_items(combo: ComboBox, items: Iterable[str]) -> None:
        combo.clear()
        combo.addItems(list(items))
        combo.setCurrentIndex(0)

    def input_text(self) -> str:
        return self.input_edit.toPlainText()

    def output_text(self) -> str:
        return self.output_edit.toPlainText()

    def selected_encoding(self) -> str:
        return self.encoding_combo.currentText()

    def is_url_safe(self) -> bool:
        return self.url_safe_check.isChecked()

    def should_fix_padding(self) -> bool:
        return self.fix_padding_check.isChecked()

    def set_input_text(self, value: str) -> None:
        self.input_edit.setPlainText(value)

    def set_output_text(self, value: str) -> None:
        self.output_edit.setPlainText(value)

    def clear_text(self) -> None:
        self.input_edit.clear()
        self.output_edit.clear()

    def focus_input(self) -> None:
        self.input_edit.setFocus()

    def crypto_algorithm(self) -> str:
        return self.crypto_algorithm_combo.currentText()

    def crypto_key_mode(self) -> str:
        return self.crypto_key_mode_combo.currentText()

    def crypto_key_encoding(self) -> str:
        return self.crypto_key_encoding_combo.currentText()

    def crypto_output_encoding(self) -> str:
        return self.crypto_output_encoding_combo.currentText()

    def crypto_text_encoding(self) -> str:
        return self.crypto_text_encoding_combo.currentText()

    def crypto_secret(self) -> str:
        return self.crypto_secret_edit.text()

    def crypto_aad(self) -> str:
        return self.crypto_aad_edit.text()

    def crypto_input(self) -> str:
        return self.crypto_input_edit.toPlainText()

    def crypto_output(self) -> str:
        return self.crypto_output_edit.toPlainText()

    def set_crypto_secret(self, value: str) -> None:
        self.crypto_secret_edit.setText(value)

    def set_crypto_output(self, value: str) -> None:
        self.crypto_output_edit.setPlainText(value)

    def clear_crypto(self) -> None:
        self.crypto_input_edit.clear()
        self.crypto_output_edit.clear()
        self.crypto_secret_edit.clear()
        self.crypto_aad_edit.clear()

    def focus_crypto_input(self) -> None:
        self.crypto_input_edit.setFocus()

    def crc_algorithm(self) -> str:
        return self.crc_algorithm_combo.currentText()

    def crc_encoding(self) -> str:
        return self.crc_encoding_combo.currentText()

    def crc_input(self) -> str:
        return self.crc_input_edit.toPlainText()

    def crc_expected(self) -> str:
        return self.crc_expected_edit.text()

    def crc_output(self) -> str:
        return self.crc_output_edit.toPlainText()

    def set_crc_output(self, value: str) -> None:
        self.crc_output_edit.setPlainText(value)

    def clear_crc(self) -> None:
        self.crc_input_edit.clear()
        self.crc_expected_edit.clear()
        self.crc_output_edit.clear()

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

    def _update_base64_counts(self) -> None:
        self.input_count_label.setText(f"{len(self.input_text())} 个字符")
        self.output_count_label.setText(f"{len(self.output_text())} 个字符")

    def _update_crypto_fields(self) -> None:
        raw_mode = self.crypto_key_mode() == "原始密钥"
        self.crypto_key_encoding_label.setVisible(raw_mode)
        self.crypto_key_encoding_combo.setVisible(raw_mode)
        self.crypto_generate_button.setVisible(raw_mode)

        algorithm = self.crypto_algorithm()
        authenticated = algorithm.endswith("GCM") or algorithm == "ChaCha20-Poly1305"
        self.crypto_aad_label.setVisible(authenticated)
        self.crypto_aad_edit.setVisible(authenticated)
        if algorithm.endswith("CBC"):
            self.crypto_warning_label.setText(
                "安全提示：CBC 仅用于兼容，不提供密文完整性认证；优先使用 AES-GCM。"
            )
        else:
            self.crypto_warning_label.setText("认证加密模式可检测错误密钥或密文篡改。")


Base64View = CryptoToolView
