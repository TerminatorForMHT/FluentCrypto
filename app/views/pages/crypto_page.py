"""现代对称加密页面。"""

from typing import Iterable

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout
from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    CardWidget,
    ComboBox,
    FluentIcon as FIF,
    LineEdit,
    PasswordLineEdit,
    PrimaryPushButton,
    PushButton,
    ScrollArea,
    StrongBodyLabel,
    SubtitleLabel,
    TextEdit,
)

from app.views.common import (
    add_action_buttons,
    create_dual_editor_layout,
    create_page_layout,
)


class CryptoPage(ScrollArea):
    """现代对称加密页面，自包含控件与事件信号。"""

    encrypt_requested = pyqtSignal()
    decrypt_requested = pyqtSignal()
    generate_key_requested = pyqtSignal()
    copy_requested = pyqtSignal()
    clear_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._create_controls()
        self._build_ui()
        self._connect_signals()
        self._update_crypto_fields()

    def _create_controls(self) -> None:
        self.algorithm_combo = ComboBox(self)
        self.key_mode_combo = ComboBox(self)
        self.key_encoding_combo = ComboBox(self)
        self.output_encoding_combo = ComboBox(self)
        self.text_encoding_combo = ComboBox(self)
        self.secret_edit = PasswordLineEdit(self)
        self.secret_edit.setPlaceholderText("请输入密码或原始密钥")
        self.aad_edit = LineEdit(self)
        self.aad_edit.setPlaceholderText("可选的附加认证数据")
        self.input_edit = TextEdit(self)
        self.output_edit = TextEdit(self)
        self.warning_label = CaptionLabel("", self)
        self.key_encoding_label = StrongBodyLabel("密钥格式", self)
        self.aad_label = StrongBodyLabel("AAD", self)
        self.generate_button = PushButton(FIF.ADD, "生成密钥", self)

    def _build_ui(self) -> None:
        layout = create_page_layout(self, "cryptoPage")
        layout.addWidget(SubtitleLabel("现代对称加密", self))
        layout.addWidget(
            BodyLabel("使用现代对称算法加密文本；输出为不含密钥的 JSON envelope。", self)
        )
        layout.addWidget(self._create_settings_card())

        self.input_edit.setPlaceholderText("加密时输入明文，解密时输入 JSON envelope")
        self.output_edit.setPlaceholderText("加密或解密结果")
        layout.addLayout(
            create_dual_editor_layout(
                self,
                self.input_edit,
                self.output_edit,
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
            self.encrypt_requested,
            self.decrypt_requested,
            self.copy_requested,
            self.clear_requested,
        )
        add_action_buttons(actions, buttons, signals)
        layout.addLayout(actions)

    def _create_settings_card(self) -> CardWidget:
        card = CardWidget(self)
        grid = QGridLayout(card)
        grid.setContentsMargins(18, 14, 18, 14)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        grid.addWidget(StrongBodyLabel("算法", self), 0, 0)
        grid.addWidget(self.algorithm_combo, 0, 1)
        grid.addWidget(StrongBodyLabel("文本编码", self), 0, 2)
        grid.addWidget(self.text_encoding_combo, 0, 3)
        grid.addWidget(StrongBodyLabel("密文格式", self), 0, 4)
        grid.addWidget(self.output_encoding_combo, 0, 5)
        grid.addWidget(StrongBodyLabel("密钥模式", self), 1, 0)
        grid.addWidget(self.key_mode_combo, 1, 1)
        grid.addWidget(self.key_encoding_label, 1, 2)
        grid.addWidget(self.key_encoding_combo, 1, 3)
        grid.addWidget(StrongBodyLabel("密码 / 密钥", self), 2, 0)
        grid.addWidget(self.secret_edit, 2, 1, 1, 4)
        grid.addWidget(self.generate_button, 2, 5)
        grid.addWidget(self.aad_label, 3, 0)
        grid.addWidget(self.aad_edit, 3, 1, 1, 5)
        grid.addWidget(self.warning_label, 4, 0, 1, 6)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        grid.setColumnStretch(5, 1)
        return card

    def _connect_signals(self) -> None:
        self.algorithm_combo.currentIndexChanged.connect(self._update_crypto_fields)
        self.key_mode_combo.currentIndexChanged.connect(self._update_crypto_fields)
        self.generate_button.clicked.connect(self.generate_key_requested.emit)

    def _update_crypto_fields(self) -> None:
        raw_mode = self.key_mode() == "原始密钥"
        self.key_encoding_label.setVisible(raw_mode)
        self.key_encoding_combo.setVisible(raw_mode)
        self.generate_button.setVisible(raw_mode)

        algorithm = self.algorithm()
        authenticated = algorithm.endswith("GCM") or algorithm == "ChaCha20-Poly1305"
        self.aad_label.setVisible(authenticated)
        self.aad_edit.setVisible(authenticated)
        if algorithm.endswith("CBC"):
            self.warning_label.setText(
                "安全提示：CBC 仅用于兼容，不提供密文完整性认证；优先使用 AES-GCM。"
            )
        else:
            self.warning_label.setText("认证加密模式可检测错误密钥或密文篡改。")

    def set_options(
        self,
        algorithms: Iterable[str],
        key_modes: Iterable[str],
        binary_encodings: Iterable[str],
        text_encodings: Iterable[str],
    ) -> None:
        self._set_combo_items(self.algorithm_combo, algorithms)
        self._set_combo_items(self.key_mode_combo, key_modes)
        self._set_combo_items(self.key_encoding_combo, binary_encodings)
        self._set_combo_items(self.output_encoding_combo, binary_encodings)
        self._set_combo_items(self.text_encoding_combo, text_encodings)
        self._update_crypto_fields()

    @staticmethod
    def _set_combo_items(combo: ComboBox, items: Iterable[str]) -> None:
        combo.clear()
        combo.addItems(list(items))
        combo.setCurrentIndex(0)

    def algorithm(self) -> str:
        return self.algorithm_combo.currentText()

    def key_mode(self) -> str:
        return self.key_mode_combo.currentText()

    def key_encoding(self) -> str:
        return self.key_encoding_combo.currentText()

    def output_encoding(self) -> str:
        return self.output_encoding_combo.currentText()

    def text_encoding(self) -> str:
        return self.text_encoding_combo.currentText()

    def secret(self) -> str:
        return self.secret_edit.text()

    def aad(self) -> str:
        return self.aad_edit.text()

    def input_text(self) -> str:
        return self.input_edit.toPlainText()

    def output_text(self) -> str:
        return self.output_edit.toPlainText()

    def set_secret(self, value: str) -> None:
        self.secret_edit.setText(value)

    def set_output_text(self, value: str) -> None:
        self.output_edit.setPlainText(value)

    def clear(self) -> None:
        self.input_edit.clear()
        self.output_edit.clear()
        self.secret_edit.clear()
        self.aad_edit.clear()

    def focus_input(self) -> None:
        self.input_edit.setFocus()
