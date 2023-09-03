from tanjun import Component, as_slash_command
from tanjun.abc import SlashContext


component = Component(name=__name__)


@component.with_slash_command
@as_slash_command("info", "このBotの情報を表示します。")
async def info_command(ctx: SlashContext) -> None:
    await ctx.respond(
        "tasurenのグローバルチャットのサンプルプログラムです。\n"
        "リポジトリ：https://github.com/tasuren/hikari-simple-global-chat"
    )


loader = component.make_loader()
