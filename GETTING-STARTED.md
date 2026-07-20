---
title: "Getting Started — 段階的セットアップガイド"
type: "reference"
status: "completed"
tags: ["setup", "onboarding"]
created: 2026-07-19
updated: 2026-07-20
---

# Getting Started — 焦らず 1 段ずつ

このテンプレートは **コアエージェント 1 体(Codex CLI)+ Hermes** で動きます([[AGENTS.md]] §0)。
**全部を一度にセットアップする必要はありません** — Obsidian + Codex CLI だけでも動きますし、外部接続(Slack / Google / GitHub など)は後から 1 本ずつ足せます。

**personal knowledge base が挫折する最大の原因は、外部ツールとの繋ぎ込みを最初に全部やろうとすること**です。このガイドは「今日から使い始めて、価値を感じた接続だけ後から足す」順序で構成しています。

```
Level 0 ── Obsidian + Codex CLI(15分・ここまでで十分使える)
Level 1 ── + Hermes 本体(外部接続の土台)
Level 2 ── + 外部接続を 1 本ずつ(Meta/connections/ 参照)
```

各 Level は独立して価値があります。**次の Level に進むのは、今の Level が日常に馴染んでから**で構いません。

---

## Level 0 — Obsidian + コアエージェント CLI(15分)

外部接続ゼロでも、この vault の中核(Daily ハブ・ノート規約・skill 群)は全部動きます。コアエージェントは **Codex** が契約([[AGENTS.md]])に従って動きます。

### 手順

1. **clone してリネーム**

   ```bash
   git clone https://github.com/your-org/claudian-orchestra-template.git my-vault
   cd my-vault
   ```

2. **Obsidian で開く**:`Open folder as vault` でこのディレクトリを選ぶ。`.obsidian/` に最小設定が入っています。

3. **コアエージェントを起動**:vault のルートで `codex` を実行します。Codex は `AGENTS.md`(ルート＋各ドメイン直下)と `.codex/skills/` を直接検出します。

4. **最初の 1 日を回してみる**:コアエージェントに日本語でこう頼むだけです。

   ```text
   今日の Daily ノートを作って
   ```

   `Daily/{今日の日付}.md` が作られ、`## 🤖 ジョブリスト` セクションが付きます。以降は Daily を見ながら「○○やって」と指示するのが基本の運用ループです。

   > **Daily はこの vault の「人間の監査点」です。** エージェントがやったこと（取り込み・集約・蒸留・チェック）はすべて Daily に痕跡として集まるので、1 日の終わりに Daily を読むだけで「何が入り、どこへ蒸留されたか」を全部確認・承認できます。

5. **自分用に最低限の書き換え**
   - `Persona/AGENTS.md` に自分のプロフィールを書く
   - `Wiki/` に最初のノートを 1 枚書いてみる(コアエージェントに「Wiki にノートを作って」と頼めば規約に沿って作ってくれます)

### Hermes なしでの運用(capture extension)

Hermes がなくても Inbox パイプラインは使えます。Inbox の single-writer を守るため、Obsidian Web Clipper / AI Exporter / Local REST API などの capture extension を入口にします。ユーザーとコアは Inbox へ直接ファイルを書きません:

- Web 記事のメモ → `Inbox/{date}/clippings/{slug}.md`
- 会議メモ → `Inbox/{capture-date}/mtgs/{provider}-{slug}.md`
- ChatGPT / Claude 等の壁打ちログ → `Inbox/{date}/chat-logs/{provider}-{slug}.md`

capture 後にコアエージェントへ「clippings 集約やって」と言えば、`inbox-aggregate` skill が Daily に集約します。保存先が最初から完全に見えている curated note は Inbox を経ずコアが Main DB に直接置き、Daily に監査記録を残します。

> **ここまでで PKM としては完成しています。** Level 1 以降は「手動でやっていることの自動化」です。

---

## Level 1 — + Hermes 本体(外部接続の土台)

ここからが「外部ツールとの繋ぎ込み」です。**認証を伴う外部接続(Slack / Google / GitHub / Notion / Genspark 等)は Hermes が一元所有**し、コアエージェントはそれらの API を直接叩きません。例外は vault 自身の local git、コアの Web research read、認証を Hermes と共有しない capture extension です([[.codex/rules/agent-boundaries.md]] §6)。

1. [Hermes Agent](https://github.com/NousResearch/Hermes-Agent) をインストール(upstream の手順に従う)
2. vault ルートから、追跡済み設定と capture skill の両方を読む per-vault profile を選ぶ:

   ```bash
   export HERMES_HOME="$PWD/.hermes"
   ```

   この profile を upstream 手順に従って初期化する。ここに作られる runtime state、upstream skill、secret は `.gitignore` 対象。既存の global `${HERMES_HOME}` を使う場合は、`.hermes/config.yaml` と `.hermes/skills/vault-capture/` **両方**を active profile に merge / mirror する。config だけの copy では capture skill が discovery されない。
3. Hermes の backend は既定で `openai-codex`。具体的な model は `hermes model` で選択（テンプレートでは固定しない）
4. 同じ `HERMES_HOME` を export した shell で動作確認:

   ```bash
   test -f "$HERMES_HOME/skills/vault-capture/inbox-daily-capture/SKILL.md"
   hermes chat -q "こんにちは。自己紹介して" -Q
   ```

   応答が返れば Hermes 本体は動いています。**この時点ではまだどの外部サービスにも繋がっていません** — それは Level 2 で 1 本ずつやります。

---

## Level 2 — 外部接続を 1 本ずつ

**いちばん簡単な方法:コアエージェントにこう言ってください。**

```text
接続セットアップして
```

`connection-setup` skill([[.codex/skills/connection-setup/SKILL.md]])が対話式ウィザードとして動きます:

1. 「仕事の会話は Slack?」「予定は Google Calendar?」のように**ユースケースで質問**(ツール名を知らなくても答えられます)
2. あなたが**使うツールだけ**を `.codex/connections.yaml` に記録(使わないものは以後ジョブリストにも診断にも出ません)
3. 選んだ接続を推奨順に **1 本ずつ、動作確認しながら**ガイド(途中でやめても再実行で続きから)

**一度に全部やらないでください。** 1 本繋いだら数日運用して馴染んでから次に進むのがおすすめです(ウィザードも 1 本ごとに「ここで止める?」と聞きます)。

手動で進めたい場合の接続ごとの手順・動作確認・トラブルシューティングは [`Meta/connections/`](./Meta/connections/README.md) にあります。

### 推奨順序

| 順 | 接続 | 難易度 | 所要 | 得られるもの | ガイド |
|---|---|---|---|---|---|
| ① | **GitHub** | ★☆☆ | 10分 | コード変化の EOD capture。**PAT 1 本で済むので、Hermes → Inbox パイプライン全体の動作確認に最適** | [Meta/connections/github.md](./Meta/connections/github.md) |
| ② | **Google カレンダー + Tasks** | ★★☆ | 30–60分 | 朝の briefing 自動化(この vault の一番おいしい部分)。Calendar だけなら ics 経路 10 分 | [Meta/connections/google-calendar-tasks.md](./Meta/connections/google-calendar-tasks.md) |
| ③ | **Gmail / Google Drive** | ★☆☆ | 各10分 | メール検索・共有資料の read(② の OAuth 基盤のついでに) | [gmail.md](./Meta/connections/gmail.md) / [google-drive.md](./Meta/connections/google-drive.md) |
| ④ | **Slack / Discord** | ★★★ | 30–60分 | 業務・コミュニティ会話の日次ダイジェストが vault に残る | [slack.md](./Meta/connections/slack.md) / [discord.md](./Meta/connections/discord.md) |
| ⑤+ | RSS / Web クリッピング / AI 議事録 / Zotero / Notion | ★☆☆〜★★☆ | 各10–30分 | 購読フィード / 記事・AI 壁打ち / 会議文字起こし / 文献管理 / 清書 publish | [Meta/connections/README.md](./Meta/connections/README.md) |

④ 以降は完全に任意です。**使わない接続の capture skill(`.hermes/skills/vault-capture/` 配下)は削除して構いません。**

### 接続の状態がわからなくなったら

コアエージェントに頼んでください:

```text
接続チェックして
```

`connection-doctor` skill([[.codex/skills/connection-doctor/SKILL.md]])が各接続を診断し、「どこが繋がっていて、どこが切れていて、次に何をすべきか」を表で報告します。

---

## つまずいたら

1. まず「接続チェックして」で切り分け(上記)
2. 各接続ガイドの「よくある躓き」セクションを見る([`Meta/connections/`](./Meta/connections/README.md))
3. それでも駄目なら、コアエージェントにエラーメッセージを貼って相談 — vault の設計を理解した状態で一緒にデバッグしてくれます

## 関連

- [[README.md]] — アーキテクチャ全景 / [[AGENTS.md]] — コア契約(§0 コア構成)
- [[Meta/connections/README.md]] — 接続別セットアップガイド
- [[.codex/rules/agent-boundaries.md]] — なぜ外部接続は Hermes 一元所有なのか
- [[.codex/rules/inbox-routing.md]] — capture → Daily → Main DB の流れ
