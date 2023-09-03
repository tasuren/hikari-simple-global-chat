from pydantic import BaseModel, Field


class MuteState(BaseModel):
    "ミュートされているチャンネルやユーザーを記録するためのクラス"

    channel_ids: set[int] = Field(default_factory=set)
    user_ids: set[int] = Field(default_factory=set)

    def clear(self) -> None:
        "初期化します。"
        self.channel_ids.clear()
        self.user_ids.clear()


class State(BaseModel):
    "状態管理をするためのクラス"

    mute: MuteState = Field(default_factory=MuteState)
    lockdown: bool = False

    def clear(self) -> None:
        "初期化します。"
        self.mute.clear()
        self.lockdown = False
