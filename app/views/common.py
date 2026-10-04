"""View 层共享的界面构建辅助函数。"""

from typing import Optional, Sequence

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    CaptionLabel,
    CardWidget,
    ScrollArea,
    StrongBodyLabel,
    TextEdit,
)


def create_page_layout(page: ScrollArea, object_name: str) -> QVBoxLayout:
    """初始化透明背景的滚动页面并返回内容布局。"""
    page.setObjectName(object_name)
    page.setWidgetResizable(True)
    page.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    page.setStyleSheet("QScrollArea { border: none; background: transparent; }")
    content = QWidget()
    content.setObjectName(f"{object_name}Content")
    content.setStyleSheet(
        f"QWidget#{object_name}Content {{ background: transparent; }}"
    )
    layout = QVBoxLayout(content)
    layout.setContentsMargins(28, 24, 28, 24)
    layout.setSpacing(14)
    page.setWidget(content)
    return layout


def create_dual_editor_layout(
    parent: QWidget,
    input_editor: TextEdit,
    output_editor: TextEdit,
    input_placeholder: str,
    output_placeholder: str,
    input_count: Optional[CaptionLabel] = None,
    output_count: Optional[CaptionLabel] = None,
) -> QGridLayout:
    """创建左右对称的输入/输出编辑卡片布局。"""
    layout = QGridLayout()
    layout.setHorizontalSpacing(16)
    layout.addWidget(
        create_editor_card(parent, "输入", input_editor, input_placeholder, input_count),
        0,
        0,
    )
    layout.addWidget(
        create_editor_card(parent, "输出", output_editor, output_placeholder, output_count),
        0,
        1,
    )
    layout.setColumnStretch(0, 1)
    layout.setColumnStretch(1, 1)
    return layout


def create_editor_card(
    parent: QWidget,
    title: str,
    editor: TextEdit,
    placeholder: str,
    count_label: Optional[CaptionLabel] = None,
) -> CardWidget:
    """创建带标题与可选字符计数的编辑器卡片。"""
    card = CardWidget(parent)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(16, 14, 16, 16)
    header = QHBoxLayout()
    header.addWidget(StrongBodyLabel(title, parent))
    header.addStretch(1)
    if count_label is not None:
        header.addWidget(count_label)
    layout.addLayout(header)
    editor.setPlaceholderText(placeholder)
    editor.setAcceptRichText(False)
    layout.addWidget(editor, 1)
    return card


def add_action_buttons(layout: QHBoxLayout, buttons: Sequence, signals: Sequence) -> None:
    """把按钮居中排布并连接到对应信号。"""
    layout.addStretch(1)
    for button, signal in zip(buttons, signals):
        button.clicked.connect(signal.emit)
        layout.addWidget(button)
    layout.addStretch(1)
