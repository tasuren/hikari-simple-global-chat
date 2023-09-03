# Simple Global Chat with Hikari
DiscordのAPIラッパhikariを使った、ちょっとしたグローバルチャットのプログラムのリポジトリです。  
tasurenがhikariを試してみたかったから作ったものです。

## 仕様
- 一つのBotにつき一つのグローバルチャットまで
- 必要な特権インテントはメッセージコンテンツ
- 恒久的なBAN設定
- Botも送信可能にする設定
- スラッシュコマンドによる一時的なモデレーション
  - ユーザーまたはチャンネルのミュート
  - ロックダウン

## 要件
- Python 3.11

## 起動方法
1. `config.template.toml`の通りに設定ファイル`config.toml`を作成（またはpydantic-settingsの仕様通りに環境変数を設定）
2. 開発時は`pdm run python3 .`、本番時は`python3 . -OO`で起動（が好ましい）

## ライセンス
ここにあるものは[このファイル]()に記載されているライセンスの下で提供されています。
