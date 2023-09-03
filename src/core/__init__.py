__all__ = ("config", "Config", "State", "logger", "load")

from typing import Final

from logging import getLogger

from .config import Config, load, config
from .state import State


logger: Final = getLogger("core")
