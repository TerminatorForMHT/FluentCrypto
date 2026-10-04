"""设置页面。"""

from typing import Dict, Iterable, Tuple

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QPushButton, QVBoxLayout
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    ComboBox,
    PushButton,
    ScrollArea,
    StrongBodyLabel,
    SubtitleLabel,
    SwitchButton,
)

from app.views.common import create_page_layout

# 与设置模型 SettingsModel.PRESET_COLORS 保持一致
PRESET_COLORS: Tuple[str, ...] = (
    "#0078D4",
    "#00B7C3",
    "#107C10",
    "#FF8C00",
    "#E81123",
    "#8661C5",
    "#E3008C",
    "#69797E",
)


class SettingsPage(ScrollArea):
    """应用外观与行为设置页面。"""

    theme_changed = pyqtSignal(int)
    theme_color_changed = pyqtSignal(str)
    always_on_top_changed = pyqtSignal(bool)
    default_page_changed = pyqtSignal(str)
    auto_copy_changed = pyqtSignal(bool)
    reset_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._color_buttons: Dict[str, QPushButton] = {}
        self._create_controls()
        self._build_ui()
        self._connect_signals()

    def _create_controls(self) -> None:
        self.theme_combo = ComboBox(self)
        self.theme_combo.addItems(["跟随系统", "浅色", "深色"])
        self.default_page_combo = ComboBox(self)
        self.always_on_top_switch = SwitchButton("关", self)
        self.always_on_top_switch.setOnText("开")
        self.always_on_top_switch.setOffText("关")
        self.auto_copy_switch = SwitchButton("关", self)
        self.auto_copy_switch.setOnText("开")
        self.auto_copy_switch.setOffText("关")
        self.reset_button = PushButton("恢复默认设置", self)

    def _build_ui(self) -> None:
        layout = create_page_layout(self, "settingsPage")
        layout.addWidget(SubtitleLabel("设置", self))
        layout.addWidget(BodyLabel("调整应用的外观与行为选项，设置会自动保存。", self))
        layout.addWidget(self._create_appearance_card())
        layout.addWidget(self._create_behavior_card())
        layout.addWidget(self._create_window_card())
        layout.addWidget(self.reset_button, 0)
        layout.addStretch(1)

    def _create_appearance_card(self) -> CardWidget:
        card = CardWidget(self)
        grid = QGridLayout(card)
        grid.setContentsMargins(18, 14, 18, 14)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)
        grid.addWidget(StrongBodyLabel("应用主题", self), 0, 0)
        grid.addWidget(self.theme_combo, 0, 1)
        grid.addWidget(StrongBodyLabel("主题色", self), 1, 0)
        grid.addLayout(self._create_color_row(), 1, 1)
        grid.setColumnStretch(2, 1)
        return card

    def _create_color_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        for color in PRESET_COLORS:
            button = QPushButton(self)
            button.setFixedSize(30, 30)
            button.setStyleSheet(self._color_style(color, selected=False))
            button.clicked.connect(
                lambda _checked=False, value=color: self.theme_color_changed.emit(value)
            )
            self._color_buttons[color] = button
            row.addWidget(button)
        row.addStretch(1)
        return row

    @staticmethod
    def _color_style(color: str, selected: bool) -> str:
        border = "2px solid #FFFFFF" if selected else "2px solid rgba(128, 128, 128, 0.4)"
        return (
            f"QPushButton {{ background: {color}; border-radius: 15px; border: {border}; }}"
            f"QPushButton:hover {{ border: 2px solid #FFFFFF; }}"
        )

    def _create_behavior_card(self) -> CardWidget:
        card = CardWidget(self)
        grid = QGridLayout(card)
        grid.setContentsMargins(18, 14, 18, 14)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)
        grid.addWidget(StrongBodyLabel("默认启动页", self), 0, 0)
        grid.addWidget(self.default_page_combo, 0, 1)
        grid.addWidget(StrongBodyLabel("完成操作后自动复制结果", self), 1, 0)
        grid.addWidget(self.auto_copy_switch, 1, 1)
        grid.setColumnStretch(2, 1)
        return card

    def _create_window_card(self) -> CardWidget:
        card = CardWidget(self)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.addWidget(StrongBodyLabel("窗口置顶", self))
        layout.addStretch(1)
        layout.addWidget(self.always_on_top_switch)
        return card

    def _connect_signals(self) -> None:
        self.theme_combo.currentIndexChanged.connect(self.theme_changed.emit)
        self.default_page_combo.currentTextChanged.connect(self.default_page_changed.emit)
        self.always_on_top_switch.checkedChanged.connect(self.always_on_top_changed.emit)
        self.auto_copy_switch.checkedChanged.connect(self.auto_copy_changed.emit)
        self.reset_button.clicked.connect(self.reset_requested.emit)

    def init_settings(
        self,
        theme: int,
        theme_color: str,
        always_on_top: bool,
        default_page: str,
        page_names: Iterable[str],
        auto_copy: bool,
    ) -> None:
        """设置初始状态（不触发任何信号）。"""
        widgets = (
            self.theme_combo,
            self.default_page_combo,
            self.always_on_top_switch,
            self.auto_copy_switch,
        )
        for widget in widgets:
            widget.blockSignals(True)
        self.theme_combo.setCurrentIndex(theme)
        self.default_page_combo.clear()
        self.default_page_combo.addItems(list(page_names))
        index = self.default_page_combo.findText(default_page)
        self.default_page_combo.setCurrentIndex(index if index >= 0 else 0)
        self.always_on_top_switch.setChecked(always_on_top)
        self.auto_copy_switch.setChecked(auto_copy)
        self.set_theme_color(theme_color)
        for widget in widgets:
            widget.blockSignals(False)

    def set_theme_color(self, color: str) -> None:
        """更新主题色色块的选中状态。"""
        for value, button in self._color_buttons.items():
            button.setStyleSheet(self._color_style(value, selected=(value == color)))
