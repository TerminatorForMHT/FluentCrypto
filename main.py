"""FluentCrypto 密码学编码校验工具入口。"""

import os
import sys

os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

from PyQt5.QtCore import QLocale, Qt
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator, Theme, setTheme, setThemeColor

from app.controller import AppController


def main() -> int:
    """创建并启动桌面应用。"""
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setApplicationName("Crypto Tool")
    app.setApplicationDisplayName("密码学编码校验工具")

    translator = FluentTranslator(QLocale.system())
    app.installTranslator(translator)

    setTheme(Theme.AUTO)
    setThemeColor("#0078D4")

    controller = AppController()
    controller.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
