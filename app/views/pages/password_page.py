"""随机密码生成页面。"""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout
from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    CardWidget,
    CheckBox,
    FluentIcon as FIF,
    LineEdit,
    PrimaryPushButton,
    PushButton,
    ScrollArea,
    SpinBox,
    StrongBodyLabel,
    SubtitleLabel,
)

from app.views.common import create_page_layout

# 与服务层 password_service.MIN_LENGTH / MAX_LENGTH / DEFAULT_LENGTH 保持一致
MIN_LENGTH = 4
MAX_LENGTH = 128
DEFAULT_LENGTH = 16


class PasswordPage(ScrollArea):
    """随机密码生成页面，自包含控件与事件信号。"""

    generate_requested = pyqtSignal()
    copy_requested = pyqtSignal()
    options_changed = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._create_controls()
        self._build_ui()
        self._connect_signals()

    def _create_controls(self) -> None:
        self.length_spin = SpinBox(self)
        self.length_spin.setRange(MIN_LENGTH, MAX_LENGTH)
        self.length_spin.setValue(DEFAULT_LENGTH)
        self.lower_check = CheckBox("小写字母 a-z", self)
        self.upper_check = CheckBox("大写字母 A-Z", self)
        self.digits_check = CheckBox("数字 0-9", self)
        self.symbols_check = CheckBox("符号 !@#$…", self)
        self.ambiguous_check = CheckBox("排除易混淆字符 0 O 1 l I", self)
        for check in (
            self.lower_check,
            self.upper_check,
            self.digits_check,
            self.symbols_check,
        ):
            check.setChecked(True)
        self.output_edit = LineEdit(self)
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText("点击生成按钮创建密码")
        self.strength_label = CaptionLabel("", self)

    def _build_ui(self) -> None:
        layout = create_page_layout(self, "passwordPage")
        layout.addWidget(SubtitleLabel("随机密码生成器", self))
        layout.addWidget(
            BodyLabel("使用加密安全随机数生成密码，可直接配合对称加密页使用。", self)
        )
        layout.addWidget(self._create_settings_card())
        layout.addWidget(self._create_result_card())

        actions = QHBoxLayout()
        self.generate_button = PrimaryPushButton(FIF.SYNC, "生成密码", self)
        self.copy_button = PushButton(FIF.COPY, "复制密码", self)
        actions.addStretch(1)
        actions.addWidget(self.generate_button)
        actions.addWidget(self.copy_button)
        actions.addStretch(1)
        layout.addLayout(actions)
        layout.addStretch(1)

    def _create_settings_card(self) -> CardWidget:
        card = CardWidget(self)
        grid = QGridLayout(card)
        grid.setContentsMargins(18, 14, 18, 14)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)
        grid.addWidget(StrongBodyLabel("长度", self), 0, 0)
        grid.addWidget(self.length_spin, 0, 1)
        grid.addWidget(self.lower_check, 1, 0)
        grid.addWidget(self.upper_check, 1, 1)
        grid.addWidget(self.digits_check, 2, 0)
        grid.addWidget(self.symbols_check, 2, 1)
        grid.addWidget(self.ambiguous_check, 3, 0, 1, 2)
        grid.setColumnStretch(2, 1)
        return card

    def _create_result_card(self) -> CardWidget:
        card = CardWidget(self)
        grid = QGridLayout(card)
        grid.setContentsMargins(18, 14, 18, 14)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)
        grid.addWidget(StrongBodyLabel("生成结果", self), 0, 0)
        grid.addWidget(self.strength_label, 0, 1)
        grid.addWidget(self.output_edit, 1, 0, 1, 2)
        grid.setColumnStretch(1, 1)
        return card

    def _connect_signals(self) -> None:
        self.generate_button.clicked.connect(self.generate_requested.emit)
        self.copy_button.clicked.connect(self.copy_requested.emit)
        self.length_spin.valueChanged.connect(self.options_changed.emit)
        for check in (
            self.lower_check,
            self.upper_check,
            self.digits_check,
            self.symbols_check,
            self.ambiguous_check,
        ):
            check.toggled.connect(self.options_changed.emit)

    def length(self) -> int:
        return self.length_spin.value()

    def use_upper(self) -> bool:
        return self.upper_check.isChecked()

    def use_lower(self) -> bool:
        return self.lower_check.isChecked()

    def use_digits(self) -> bool:
        return self.digits_check.isChecked()

    def use_symbols(self) -> bool:
        return self.symbols_check.isChecked()

    def exclude_ambiguous(self) -> bool:
        return self.ambiguous_check.isChecked()

    def password(self) -> str:
        return self.output_edit.text()

    def set_password(self, value: str) -> None:
        self.output_edit.setText(value)

    def set_strength(self, text: str) -> None:
        self.strength_label.setText(text)
