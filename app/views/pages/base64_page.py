"""Base64 编码解码页面。"""

from typing import Iterable

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout
from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    CardWidget,
    CheckBox,
    ComboBox,
    FluentIcon as FIF,
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


class Base64Page(ScrollArea):
    """Base64 编码解码页面，自包含控件与事件信号。"""

    encode_requested = pyqtSignal()
    decode_requested = pyqtSignal()
    swap_requested = pyqtSignal()
    copy_requested = pyqtSignal()
    clear_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._create_controls()
        self._build_ui()
        self._connect_signals()

    def _create_controls(self) -> None:
        self.input_edit = TextEdit(self)
        self.output_edit = TextEdit(self)
        self.encoding_combo = ComboBox(self)
        self.url_safe_check = CheckBox("URL-safe", self)
        self.fix_padding_check = CheckBox("解码时自动补齐 padding", self)
        self.fix_padding_check.setChecked(True)
        self.input_count_label = CaptionLabel("0 个字符", self)
        self.output_count_label = CaptionLabel("0 个字符", self)

    def _build_ui(self) -> None:
        layout = create_page_layout(self, "base64Page")
        layout.addWidget(SubtitleLabel("Base64 编码解码", self))
        layout.addWidget(
            BodyLabel("快速完成文本的 Base64 编码与解码，所有数据仅在本地处理。", self)
        )
        layout.addWidget(self._create_settings_card())
        layout.addLayout(
            create_dual_editor_layout(
                self,
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
        add_action_buttons(actions, buttons, signals)
        layout.addLayout(actions)

    def _create_settings_card(self) -> CardWidget:
        card = CardWidget(self)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(12)
        layout.addWidget(StrongBodyLabel("字符编码", self))
        layout.addWidget(self.encoding_combo)
        layout.addWidget(self.url_safe_check)
        layout.addWidget(self.fix_padding_check)
        layout.addStretch(1)
        return card

    def _connect_signals(self) -> None:
        self.input_edit.textChanged.connect(self._update_counts)
        self.output_edit.textChanged.connect(self._update_counts)

    def _update_counts(self) -> None:
        self.input_count_label.setText(f"{len(self.input_text())} 个字符")
        self.output_count_label.setText(f"{len(self.output_text())} 个字符")

    def set_supported_encodings(self, encodings: Iterable[str]) -> None:
        self.encoding_combo.clear()
        self.encoding_combo.addItems(list(encodings))
        self.encoding_combo.setCurrentIndex(0)

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
