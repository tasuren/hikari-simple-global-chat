from typing import Final

from logging import getLogger

from hikari import GatewayBot, Intents, HikariInterrupt
from hikari.impl import CacheSettings
from hikari.api import CacheComponents

import tanjun

from core import State, Config, load


config = load()


intents = Intents.ALL_MESSAGES | Intents.MESSAGE_CONTENT
# 以下のインテントは、ローバルチャットで送信元のサーバーの名前をキャッシュするために必要。
intents |= Intents.GUILDS


bot: Final = GatewayBot(
    token=config.token,
    cache_settings=CacheSettings(
        components=CacheComponents.GUILDS | CacheComponents.ME,
        max_messages=0,
        max_dm_channel_ids=0,
    ),
    intents=intents,
)
logger: Final = getLogger("app")


client = (
    tanjun.Client.from_gateway_bot(bot, declare_global_commands=True)
    .load_modules("components.general")
    .load_modules("components.admin")
    .load_modules("components.logic")
    .set_type_dependency(Config, config)
    .set_type_dependency(State, State(lockdown=config.policy.first_lockdown))
)


try:
    bot.run()
except HikariInterrupt:
    pass
