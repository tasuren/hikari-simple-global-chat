from typing import Literal, TypeAlias, Final, get_args

from hikari import Embed

import tanjun
from tanjun.abc import SlashContext, Context
from alluka import Injected

from json import dumps

from core import State
from core.config import Config, load

from utils import bool_to_str, join_code


def check(ctx: Context, config: Injected[Config]) -> bool:
    return ctx.author.id in config.admin_ids


component = tanjun.Component(name=__name__)
group = component.with_slash_command(
    tanjun.slash_command_group("admin", "管理用コマンドです。")
).add_check(check)


moderation_group = group.make_sub_group("moderation", "グローバルチャットのモデレーションをします。")


@moderation_group.as_sub_command("state", "現在の管理状況を表示します。")
async def state_command(ctx: SlashContext, state: Injected[State]) -> None:
    await ctx.respond(
        embeds=(
            Embed(title="管理状況").add_field("ロックダウン", value=bool_to_str(state.lockdown)),
            Embed(description="ミュート")
            .add_field("チャンネル", value=join_code(map(str, state.mute.channel_ids)))
            .add_field("ユーザー", value=join_code(map(str, state.mute.user_ids))),
        )
    )


@moderation_group.as_sub_command("lock", "グローバルチャットをロックします。")
async def lock_command(ctx: SlashContext, state: Injected[State]) -> None:
    state.lockdown = True
    await ctx.respond("できた。")


@moderation_group.as_sub_command("unlock", "グローバルチャットをロックします。")
async def unlock_command(ctx: SlashContext, state: Injected[State]) -> None:
    state.lockdown = False
    await ctx.respond("できた。")


MuteMode: TypeAlias = Literal["ユーザー", "チャンネル"]
MUTE_MODES: Final = get_args(MuteMode)


async def mute_or_unmute(
    ctx: SlashContext,
    state: State,
    mode: Literal["mute", "unmute"],
    mute_mode: MuteMode,
    target_id: int,
) -> None:
    "ミュートまたはミュート解除を行います。"
    if mode == "mute":
        invoke = (
            state.mute.user_ids.add
            if mute_mode == "ユーザー"
            else state.mute.channel_ids.add
        )
    else:
        invoke = (
            state.mute.user_ids.remove
            if mute_mode == "ユーザー"
            else state.mute.channel_ids.remove
        )

    invoke(target_id)

    await ctx.respond("できた。")


@tanjun.with_str_slash_option("target_id", "ミュートにする対象のIDです。", converters=int)
@tanjun.with_str_slash_option("mode", "対象の種類です。", choices=MUTE_MODES)
@moderation_group.as_sub_command("mute", "チャンネルまたはユーザーをミュートします。")
async def mute_command(
    ctx: SlashContext,
    state: Injected[State],
    mode: MuteMode,
    target_id: int,
) -> None:
    await mute_or_unmute(ctx, state, "mute", mode, target_id)


@tanjun.with_str_slash_option("target_id", "ミュート解除する対象のIDです。", converters=int)
@tanjun.with_str_slash_option("mode", "対象の種類です。", choices=MUTE_MODES)
@moderation_group.as_sub_command("unmute", "チャンネルまたはユーザーをミュート解除します。")
async def unmute_command(
    ctx: SlashContext,
    state: Injected[State],
    mode: MuteMode,
    target_id: int,
) -> None:
    await mute_or_unmute(ctx, state, "unmute", mode, target_id)


@group.as_sub_command("reload", "設定を再読み込みします。")
async def reload_configuration_command(ctx: SlashContext) -> None:
    await ctx.defer()

    assert ctx.client.loop is not None
    await ctx.client.loop.run_in_executor(None, load)

    await ctx.create_followup("できた。")


loader = component.make_loader()
