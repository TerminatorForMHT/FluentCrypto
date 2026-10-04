"""应用设置模型：维护选项并持久化。"""

from dataclasses import asdict, dataclass
from typing import Tuple

from app.services.settings_store import load_settings, save_settings


@dataclass(frozen=True)
class SettingsOptions:
    """应用设置选项。"""

    theme: int = 0  # 0 跟随系统 / 1 浅色 / 2 深色
    theme_color: str = "#0078D4"
    always_on_top: bool = False
    default_page: str = "Base64"
    auto_copy: bool = False


class SettingsModel:
    """加载、保存并维护应用设置。"""

    # 与设置页 settings_page.PRESET_COLORS 保持一致
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
    PAGE_NAMES: Tuple[str, ...] = ("Base64", "对称加密", "CRC 校验", "哈希工具", "密码生成")

    def __init__(self) -> None:
        self._options = self._load()

    @property
    def options(self) -> SettingsOptions:
        return self._options

    def configure(self, **changes) -> None:
        data = asdict(self._options)
        data.update(changes)
        self._options = SettingsOptions(**data)
        save_settings(asdict(self._options))

    def reset(self) -> SettingsOptions:
        self._options = SettingsOptions()
        save_settings(asdict(self._options))
        return self._options

    def _load(self) -> SettingsOptions:
        raw = load_settings()
        try:
            options = SettingsOptions(
                theme=int(raw.get("theme", 0)),
                theme_color=str(raw.get("theme_color", "#0078D4")),
                always_on_top=bool(raw.get("always_on_top", False)),
                default_page=str(raw.get("default_page", "Base64")),
                auto_copy=bool(raw.get("auto_copy", False)),
            )
        except (TypeError, ValueError):
            return SettingsOptions()
        if options.theme not in (0, 1, 2):
            options = SettingsOptions(**{**asdict(options), "theme": 0})
        if options.default_page not in self.PAGE_NAMES:
            options = SettingsOptions(**{**asdict(options), "default_page": "Base64"})
        return options
