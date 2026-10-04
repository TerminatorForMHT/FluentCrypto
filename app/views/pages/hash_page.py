"""哈希计算页面。"""

from typing import Iterable, Tuple

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout
from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    CardWidget,
    CheckBox,
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


class HashPage(ScrollArea):
    """哈希/HMAC 计算与验证页面，自包含控件与事件信号。"""

    calculate_requested = pyqtSignal()
    verify_requested = pyqtSignal()
    copy_requested = pyqtSignal()
    clear_requested = pyqtSignal()

    # 与服务层 hash_service.INSECURE_ALGORITHMS 保持一致
    INSECURE_ALGORITHMS: Tuple[str, ...] = ("MD5", "SHA-1")

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._create_controls()
        self._build_ui()
        self._connect_signals()
        self._update_fields()

    def _create_controls(self) -> None:
        self.algorithm_combo = ComboBox(self)
        self.encoding_combo = ComboBox(self)
        self.hmac_check = CheckBox("HMAC", self)
        self.hmac_key_edit = PasswordLineEdit(self)
        self.hmac_key_edit.setPlaceholderText("请输入 HMAC 密钥")
        self.expected_edit = LineEdit(self)
        self.expected_edit.setPlaceholderText("例如 5D41402ABC4B2A76B9719D911017C592")
        self.warning_label = CaptionLabel("", self)
        self.input_edit = TextEdit(self)
        self.output_edit = TextEdit(self)
        self.output_edit.setReadOnly(True)

    def _build_ui(self) -> None:
        layout = create_page_layout(self, "hashPage")
        layout.addWidget(SubtitleLabel("哈希工具", self))
        layout.addWidget(
            BodyLabel("计算文本的哈希摘要或 HMAC；哈希是单向运算，不可逆推原文。", self)
        )
        layout.addWidget(self._create_settings_card())
        layout.addLayout(
            create_dual_editor_layout(
                self,
                self.input_edit,
                self.output_edit,
                "请输入待计算文本",
                "哈希结果",
            ),
            1,
        )

        actions = QHBoxLayout()
        buttons = (
            PrimaryPushButton(FIF.TAG, "计算", self),
            PrimaryPushButton(FIF.ACCEPT, "验证", self),
            PushButton(FIF.COPY, "复制结果", self),
            PushButton(FIF.DELETE, "清空", self),
        )
        signals = (
            self.calculate_requested,
            self.verify_requested,
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
        grid.addWidget(StrongBodyLabel("哈希算法", self), 0, 0)
        grid.addWidget(self.algorithm_combo, 0, 1)
        grid.addWidget(StrongBodyLabel("文本编码", self), 0, 2)
        grid.addWidget(self.encoding_combo, 0, 3)
        grid.addWidget(self.hmac_check, 1, 0)
        grid.addWidget(self.hmac_key_edit, 1, 1, 1, 3)
        grid.addWidget(StrongBodyLabel("期望哈希", self), 2, 0)
        grid.addWidget(self.expected_edit, 2, 1, 1, 3)
        grid.addWidget(self.warning_label, 3, 0, 1, 4)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        return card

    def _connect_signals(self) -> None:
        self.algorithm_combo.currentIndexChanged.connect(self._update_fields)
        self.hmac_check.toggled.connect(self._update_fields)

    def _update_fields(self) -> None:
        self.hmac_key_edit.setVisible(self.hmac_check.isChecked())
        if self.algorithm() in self.INSECURE_ALGORITHMS:
            self.warning_label.setText(
                f"安全提示：{self.algorithm()} 已不具备抗碰撞性，仅用于兼容校验。"
            )
        else:
            self.warning_label.setText("")

    def set_options(
        self, algorithms: Iterable[str], text_encodings: Iterable[str]
    ) -> None:
        self.algorithm_combo.clear()
        self.algorithm_combo.addItems(list(algorithms))
        self.encoding_combo.clear()
        self.encoding_combo.addItems(list(text_encodings))
        index = self.algorithm_combo.findText("SHA-256")
        self.algorithm_combo.setCurrentIndex(index if index >= 0 else 0)
        self.encoding_combo.setCurrentIndex(0)
        self._update_fields()

    def algorithm(self) -> str:
        return self.algorithm_combo.currentText()

    def encoding(self) -> str:
        return self.encoding_combo.currentText()

    def hmac_key(self) -> str:
        if not self.hmac_check.isChecked():
            return ""
        return self.hmac_key_edit.text()

    def input_text(self) -> str:
        return self.input_edit.toPlainText()

    def expected(self) -> str:
        return self.expected_edit.text()

    def output_text(self) -> str:
        return self.output_edit.toPlainText()

    def set_output_text(self, value: str) -> None:
        self.output_edit.setPlainText(value)

    def clear(self) -> None:
        self.input_edit.clear()
        self.expected_edit.clear()
        self.output_edit.clear()
