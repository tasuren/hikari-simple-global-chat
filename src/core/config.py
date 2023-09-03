__all__ = ("ENV_PREFIX", "CONFIG_PATH", "GlobalChatConfig", "Config", "config", "load")

from typing import Self

from logging import getLogger

from os import getenv
from os.path import exists

from tomllib import loads

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .state import State


ENV_PREFIX = "TGCS"
CONFIG_PATH = getenv(f"{ENV_PREFIX}_PATH_OF_CONFIG") or "config.toml"
LOGGER = getLogger(__name__)


class GlobalChatConfig(BaseSettings):
    "グローバルチャットについての設定"

    banned_user_ids: list[int] = Field(default_factory=list)
    allow_bot: bool = False
    default_state: State = Field(default_factory=State)


class Config(BaseSettings):
    "設定"

    model_config = SettingsConfigDict(
        case_sensitive=True, env_prefix=ENV_PREFIX, env_file=".env"
    )

    token: str
    admin_ids: list[int] = Field(default_factory=list)
    global_chat: GlobalChatConfig = Field(default_factory=GlobalChatConfig)

    def model_post_init(self, _) -> None:
        if not self.admin_ids:
            LOGGER.warning("管理者が指定されていません。この場合、ミュートといったコマンドは誰も使えません。")

    def update(self, new: Self) -> Self:
        self.model_fields.update(new.model_fields)
        return self


config: Config | None = None


def load() -> Config:
    """設定を読み込みます。
    一度、読み込んだことがある場合、前回のインスタンスの中身を上書きします。（つまり、IDは変わりません）"""
    global config

    if exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            tmp = Config.model_validate(loads(f.read()))
    else:
        tmp = Config(token="...", admin_ids=[])

    if config is None:
        config = tmp
    else:
        config.update(tmp)

    LOGGER.debug("読み込んだ設定：%s", config)

    return config
