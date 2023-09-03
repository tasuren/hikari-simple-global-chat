from typing import Final

from logging import getLogger

import hikari
import tanjun

from core import State, Config, load


config = load()
bot: Final = hikari.GatewayBot(token=config.token)
logger: Final = getLogger("app")


client = (
    tanjun.Client.from_gateway_bot(bot, declare_global_commands=True)
    .load_modules("components.general")
    .load_modules("components.admin")
    .set_type_dependency(Config, config)
    .set_type_dependency(State, State())
)


try:
    bot.run()
except hikari.HikariInterrupt:
    pass
