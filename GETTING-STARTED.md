---
title: "Getting Started — 段階的セットアップガイド"
type: "reference"
status: "completed"
tags: ["setup", "onboarding"]
created: 2026-07-19
updated: 2026-07-19
---

# Getting Started — 焦らず 1 段ずつ

このテンプレートは **コアエージェント 1 体(Codex 既定 / Claude Code 選択可)+ Hermes** で動きます([[AGENTS.md]] §0)。
**全部を一度にセットアップする必要はありません** — Obsidian + コアエージェント CLI だけでも動きますし、外部接続(Slack / Google / GitHub など)は後から 1 本ずつ足せます。

**personal knowledge base が挫折する最大の原因は、外部ツールとの繋ぎ込みを最初に全部やろうとすること**です。このガイドは「今日から使い始めて、価値を感じた接続だけ後から足す」順序で構成しています。

```
Level 0 ── Obsidian + コアエージェント CLI(15分・ここまでで十分使える)
Level 1 ── コアを確定(core-setup:Codex 既定 / Claude Code / 併用)
Level 2 ── + Hermes 本体(外部接続の土台)
Level 3 ── + 外部接続を 1 本ずつ(docs/connections/ 参照)
```

各 Level は独立して価値があります。**次の Level に進むのは、今の Level が日常に馴染んでから**で構いません。

---

## Level 0 — Obsidian + コアエージェント CLI(15分)

外部接続ゼロでも、この vault の中核(Daily ハブ・ノート規約・skill 群)は全部動きます。コアエージェントは **Codex(既定)** でも **Claude Code** でも同じ契約([[AGENTS.md]])で動きます。

### 手順

1. **clone してリネーム**

   ```bash
   git clone https://github.com/your-org/claudian-orchestra-template.git my-vault
   cd my-vault
   ```

2. **Obsidian で開く**:`Open folder as vault` でこのディレクトリを選ぶ。`.obsidian/` に最小設定が入っています。

3. **コアエージェントを起動**:vault のルートで CLI を実行します。
   - **Codex(既定)**:`codex` — ルートの `AGENTS.md`(運用契約)が自動で読み込まれます
   - **Claude Code**:`claude` — `CLAUDE.md`(アダプタ)経由で同じ契約が読み込まれます

4. **最初の 1 日を回してみる**:コアエージェントに日本語でこう頼むだけです。

   ```text
   今日の Daily ノートを作って
   ```

   `Daily/{今日の日付}.md` が作られ、`## 🤖 ジョブリスト` セクションが付きます。以降は Daily を見ながら「○○やって」と指示するのが基本の運用ループです。

5. **自分用に最低限の書き換え**
   - `Persona/CLAUDE.md` に自分のプロフィールを書く
   - `Work/PROJ_A/` を実案件コードにリネーム(`.claude/rules/work-management.md` の対応表も更新 — コアエージェントに「PROJ_A を ACME にリネームして」と頼めば規約ごと直してくれます)

### 外部接続なしでの運用(手動 capture)

Hermes がなくても Inbox パイプラインは使えます。**自分の手で `Inbox/{今日の日付}/{source}/` にファイルを置けばよい**だけです:

- Web 記事のメモ → `Inbox/{date}/clippings/{slug}.md` に貼り付け
- 会議メモ → `Inbox/{date}/mtgs/{slug}.md`
- ChatGPT / Claude の壁打ちログ → `Inbox/{date}/chat-logs/{slug}.md`

置いたらコアエージェントに「clippings 集約やって」と言えば、`aggregate-*` skill が Daily に集約します。夜は「EOD distill やって」で Main DB(Work / Others / Research)へ蒸留されます。

> **ここまでで PKM としては完成しています。** Level 1 以降は「手動でやっていることの自動化」です。

---

## Level 1 — コアを確定する(core-setup)

数日使って続けられそうだと思ったら、コアエージェントにこう言ってください:

```text
コアのセットアップして
```

`core-setup` skill([[.claude/skills/core-setup/SKILL.md]])が 1 問だけ聞きます — 「**Codex / Claude Code / 両方、どれを使いますか?**」。答えに応じてリポジトリを整えます(すべて承認つき・git で戻せます):

| 選択 | 何が起きるか |
|---|---|
| **Codex のみ(既定)** | `.claude/` を `.agents/` にリネーム移行(全リンク書き換え込み)し、Claude 固有ファイル(`CLAUDE.md`・settings・subagent 定義)を削除。以後は `AGENTS.md` + `.agents/` だけのクリーンな構成 |
| **Claude Code のみ** | `.codex/` を削除(`AGENTS.md` はコア契約本体なので残ります) |
| **両方(併用)** | 何も消しません。両 CLI が同じ契約・同じ制御プレーンを読みます |

> 急がなくても大丈夫です。未実施のままでも全機能動きます(その場合ジョブリスト等に案内が出ます)。

---

## Level 2 — + Hermes 本体(外部接続の土台)

ここからが「外部ツールとの繋ぎ込み」です。**すべての外部接続(Slack / Google / GitHub / Notion / Genspark 等)の認証は Hermes が一元所有**します。コアエージェントは外部 API を直接叩きません(理由は [[.claude/rules/agent-boundaries.md]] §6 — 認証の重複保有と split-brain を防ぐため)。

1. [Hermes Agent](https://github.com/NousResearch/Hermes-Agent) をインストール(upstream の手順に従う)
2. この vault の `.hermes/config.yaml` を `${HERMES_HOME}`(既定 `~/.hermes/`)の設定にマージ
3. Hermes の LLM バックエンドを設定(`config.yaml` の `model:` キー)
4. 動作確認:

   ```bash
   hermes chat -q "こんにちは。自己紹介して" -Q
   ```

   応答が返れば Hermes 本体は動いています。**この時点ではまだどの外部サービスにも繋がっていません** — それは Level 3 で 1 本ずつやります。

---

## Level 3 — 外部接続を 1 本ずつ

**いちばん簡単な方法:コアエージェントにこう言ってください。**

```text
接続セットアップして
```

`connection-setup` skill([[.claude/skills/connection-setup/SKILL.md]])が対話式ウィザードとして動きます:

1. 「仕事の会話は Slack?」「予定は Google Calendar?」のように**ユースケースで質問**(ツール名を知らなくても答えられます)
2. あなたが**使うツールだけ**を `.claude/connections.yaml` に記録(使わないものは以後ジョブリストにも診断にも出ません)
3. 選んだ接続を推奨順に **1 本ずつ、動作確認しながら**ガイド(途中でやめても再実行で続きから)

**一度に全部やらないでください。** 1 本繋いだら数日運用して馴染んでから次に進むのがおすすめです(ウィザードも 1 本ごとに「ここで止める?」と聞きます)。

手動で進めたい場合の接続ごとの手順・動作確認・トラブルシューティングは [`docs/connections/`](./docs/connections/README.md) にあります。

### 推奨順序

| 順 | 接続 | 難易度 | 所要 | 得られるもの | ガイド |
|---|---|---|---|---|---|
| ① | **GitHub** | ★☆☆ | 10分 | コード変化の EOD capture。**PAT 1 本で済むので、Hermes → Inbox パイプライン全体の動作確認に最適** | [docs/connections/github.md](./docs/connections/github.md) |
| ② | **Google カレンダー + Tasks** | ★★☆ | 30–60分 | 朝の briefing 自動化(この vault の一番おいしい部分)。Calendar だけなら ics 経路 10 分 | [docs/connections/google-calendar-tasks.md](./docs/connections/google-calendar-tasks.md) |
| ③ | **Gmail / Google Drive** | ★☆☆ | 各10分 | メール検索・共有資料の read(② の OAuth 基盤のついでに) | [gmail.md](./docs/connections/gmail.md) / [google-drive.md](./docs/connections/google-drive.md) |
| ④ | **Slack / Discord** | ★★★ | 30–60分 | 業務・コミュニティ会話の日次ダイジェストが vault に残る | [slack.md](./docs/connections/slack.md) / [discord.md](./docs/connections/discord.md) |
| ⑤+ | RSS / Web クリッピング / AI 議事録 / Zotero / Notion | ★☆☆〜★★☆ | 各10–30分 | 購読フィード / 記事・AI 壁打ち / 会議文字起こし / 文献管理 / 清書 publish | [docs/connections/README.md](./docs/connections/README.md) |

④ 以降は完全に任意です。**使わない接続の capture skill(`.hermes/skills/vault-capture/` 配下)は削除して構いません。**

### 接続の状態がわからなくなったら

コアエージェントに頼んでください:

```text
接続チェックして
```

`connection-doctor` skill([[.claude/skills/connection-doctor/SKILL.md]])が各接続を診断し、「どこが繋がっていて、どこが切れていて、次に何をすべきか」を表で報告します。

---

## つまずいたら

1. まず「接続チェックして」で切り分け(上記)
2. 各接続ガイドの「よくある躓き」セクションを見る([`docs/connections/`](./docs/connections/README.md))
3. それでも駄目なら、コアエージェントにエラーメッセージを貼って相談 — vault の設計を理解した状態で一緒にデバッグしてくれます

## 関連

- [[README.md]] — アーキテクチャ全景 / [[AGENTS.md]] — コア契約(§0 コア構成)
- [[docs/connections/README.md]] — 接続別セットアップガイド
- [[.claude/rules/agent-boundaries.md]] — なぜ外部接続は Hermes 一元所有なのか
- [[.claude/rules/inbox-routing.md]] — capture → Daily → Main DB の流れ
