"""随机密码生成模型。"""

from dataclasses import dataclass
from typing import Tuple

from app.services.password_service import (
    DEFAULT_LENGTH,
    estimate_strength,
    generate_password,
)


@dataclass(frozen=True)
class PasswordOptions:
    """密码生成选项。"""

    length: int = DEFAULT_LENGTH
    use_upper: bool = True
    use_lower: bool = True
    use_digits: bool = True
    use_symbols: bool = True
    exclude_ambiguous: bool = False


class PasswordModel:
    """维护密码生成选项并生成密码。"""

    def __init__(self) -> None:
        self._options = PasswordOptions()

    def configure(
        self,
        length: int,
        use_upper: bool,
        use_lower: bool,
        use_digits: bool,
        use_symbols: bool,
        exclude_ambiguous: bool,
    ) -> None:
        self._options = PasswordOptions(
            length,
            use_upper,
            use_lower,
            use_digits,
            use_symbols,
            exclude_ambiguous,
        )

    def generate(self) -> str:
        return generate_password(
            self._options.length,
            self._options.use_upper,
            self._options.use_lower,
            self._options.use_digits,
            self._options.use_symbols,
            self._options.exclude_ambiguous,
        )

    def strength(self) -> Tuple[str, int]:
        return estimate_strength(
            self._options.length,
            self._options.use_upper,
            self._options.use_lower,
            self._options.use_digits,
            self._options.use_symbols,
            self._options.exclude_ambiguous,
        )
