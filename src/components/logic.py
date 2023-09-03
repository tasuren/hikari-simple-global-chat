from logging import getLogger

from asyncio import gather

from hikari import MessageCreateEvent, Message, Guild, Embed
from hikari.traits import RESTAware
from hikari.api import Cache

import tanjun
from alluka import Injected

from more_itertools import chunked

from core import Config, State


logger = getLogger(__name__)
component = tanjun.Component(name=__name__)


def make_name(name: str, id_: int) -> str:
    return "%s (%d)" % (name, id_)


async def obtain_guild(app: RESTAware, cache: Cache, id_: int) -> Guild:
    if (guild := cache.get_guild(id_)) is None:
        print(1)
        guild = await app.rest.fetch_guild(id_)
    return guild


async def send(cache: Cache, message: Message, channel_id: int) -> None:
    "メッセージを送信します。"
    if message.guild_id is None:
        guild = None
    else:
        guild = await obtain_guild(message.app, cache, message.guild_id)

    await message.app.rest.create_message(
        channel_id,
        embed=Embed(description=message.content)
        .set_author(
            name=make_name(
                message.author.global_name or message.author.username, message.author.id
            ),
            icon=message.author.avatar_url,
        )
        .set_footer(
            "送信者のDM (...)" if guild is None else make_name(guild.name, guild.id),
            icon=None if guild is None else guild.icon_url,
        ),
    )


def resolve_moderation(config: Config, state: State, message: Message) -> bool:
    """モデレーションの処理をします。
    `True`を返した場合、送っても大丈夫ということです。"""
    return (
        not state.lockdown
        and message.author.id not in config.policy.banned_user_ids
        and message.author.id not in state.mute.user_ids
        and message.channel_id not in state.mute.channel_ids
        and (config.policy.allow_bot or not message.author.is_bot)
    )


@component.with_listener()
async def on_message(
    event: MessageCreateEvent,
    cache: Injected[Cache],
    config: Injected[Config],
    state: Injected[State],
) -> None:
    if (me := cache.get_me()) is None or event.message.author.id == me.id:
        return

    if event.message.channel_id not in config.channel_ids or not resolve_moderation(
        config, state, event.message
    ):
        logger.info(
            "ユーザー%sによるチャンネル%dからの送信をブロックしました。",
            make_name(
                event.message.author.global_name or event.message.author.username,
                event.message.author.id,
            ),
            event.message.channel_id,
        )
        return

    logger.info("メッセージ%dを送信しています...", event.message_id)

    for channel_ids in chunked(config.channel_ids, 5):
        logger.debug("送信中... %s", channel_ids)

        await gather(
            *(
                send(cache, event.message, channel_id)
                for channel_id in channel_ids
                if channel_id != event.message.channel_id
            )
        )

    logger.info("メッセージ%dを送信しました。", event.message_id)


loader = component.make_loader()
