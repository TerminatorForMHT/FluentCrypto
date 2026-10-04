"""CRC 校验页面。"""

from typing import Iterable

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    ComboBox,
    FluentIcon as FIF,
    LineEdit,
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


class CrcPage(ScrollArea):
    """CRC 计算与验证页面，自包含控件与事件信号。"""

    calculate_requested = pyqtSignal()
    verify_requested = pyqtSignal()
    copy_requested = pyqtSignal()
    clear_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._create_controls()
        self._build_ui()

    def _create_controls(self) -> None:
        self.algorithm_combo = ComboBox(self)
        self.encoding_combo = ComboBox(self)
        self.expected_edit = LineEdit(self)
        self.expected_edit.setPlaceholderText("例如 0xCBF43926 或十进制值")
        self.input_edit = TextEdit(self)
        self.output_edit = TextEdit(self)
        self.output_edit.setReadOnly(True)

    def _build_ui(self) -> None:
        layout = create_page_layout(self, "crcPage")
        layout.addWidget(SubtitleLabel("CRC 校验", self))
        layout.addWidget(BodyLabel("计算或验证常见 CRC 校验值；CRC 不属于加密算法。", self))
        layout.addWidget(self._create_settings_card())
        layout.addLayout(
            create_dual_editor_layout(
                self,
                self.input_edit,
                self.output_edit,
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
        grid.addWidget(StrongBodyLabel("CRC 算法", self), 0, 0)
        grid.addWidget(self.algorithm_combo, 0, 1)
        grid.addWidget(StrongBodyLabel("文本编码", self), 0, 2)
        grid.addWidget(self.encoding_combo, 0, 3)
        grid.addWidget(StrongBodyLabel("期望 CRC", self), 1, 0)
        grid.addWidget(self.expected_edit, 1, 1, 1, 3)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        return card

    def set_options(
        self, algorithms: Iterable[str], text_encodings: Iterable[str]
    ) -> None:
        self.algorithm_combo.clear()
        self.algorithm_combo.addItems(list(algorithms))
        self.algorithm_combo.setCurrentIndex(0)
        self.encoding_combo.clear()
        self.encoding_combo.addItems(list(text_encodings))
        self.encoding_combo.setCurrentIndex(0)
        index = self.algorithm_combo.findText("CRC-32/ISO-HDLC")
        if index >= 0:
            self.algorithm_combo.setCurrentIndex(index)

    def algorithm(self) -> str:
        return self.algorithm_combo.currentText()

    def encoding(self) -> str:
        return self.encoding_combo.currentText()

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
