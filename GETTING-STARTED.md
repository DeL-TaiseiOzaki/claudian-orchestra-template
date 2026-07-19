---
title: "Getting Started — 段階的セットアップガイド"
type: "reference"
status: "completed"
tags: ["setup", "onboarding"]
created: 2026-07-19
updated: 2026-07-19
---

# Getting Started — 焦らず 1 段ずつ

このテンプレートは **全部を一度にセットアップする必要はありません**。
Obsidian + Claude Code だけでも動きますし、外部接続(Slack / Google / GitHub など)は後から 1 本ずつ足せます。

**personal knowledge base が挫折する最大の原因は、外部ツールとの繋ぎ込みを最初に全部やろうとすること**です。このガイドは「今日から使い始めて、価値を感じた接続だけ後から足す」順序で構成しています。

```
Level 0 ── Obsidian + Claude Code だけ(15分・ここまでで十分使える)
Level 1 ── + Codex(コード作業の委譲)
Level 2 ── + Hermes 本体(外部接続の土台)
Level 3 ── + 外部接続を 1 本ずつ(docs/connections/ 参照)
```

各 Level は独立して価値があります。**次の Level に進むのは、今の Level が日常に馴染んでから**で構いません。

---

## Level 0 — Obsidian + Claude Code(15分)

外部接続ゼロでも、この vault の中核(Daily ハブ・ノート規約・skill 群)は全部動きます。

### 手順

1. **clone してリネーム**

   ```bash
   git clone https://github.com/your-org/claudian-orchestra-template.git my-vault
   cd my-vault
   ```

2. **Obsidian で開く**:`Open folder as vault` でこのディレクトリを選ぶ。`.obsidian/` に最小設定が入っています。

3. **Claude Code を起動**:vault のルートで `claude` を実行。`CLAUDE.md` が自動で読み込まれ、vault の運用契約を理解した状態で立ち上がります。

4. **最初の 1 日を回してみる**:Claude Code に日本語でこう頼むだけです。

   ```text
   今日の Daily ノートを作って
   ```

   `Daily/{今日の日付}.md` が作られ、`## 🤖 ジョブリスト` セクションが付きます。以降は Daily を見ながら「○○やって」と指示するのが基本の運用ループです。

5. **自分用に最低限の書き換え**
   - `Persona/CLAUDE.md` に自分のプロフィールを書く
   - `Work/PROJ_A/` を実案件コードにリネーム(`.claude/rules/work-management.md` の対応表も更新 — Claude に「PROJ_A を ACME にリネームして」と頼めば規約ごと直してくれます)

### 外部接続なしでの運用(手動 capture)

Hermes がなくても Inbox パイプラインは使えます。**自分の手で `Inbox/{今日の日付}/{source}/` にファイルを置けばよい**だけです:

- Web 記事のメモ → `Inbox/{date}/clippings/{slug}.md` に貼り付け
- 会議メモ → `Inbox/{date}/mtgs/{slug}.md`
- ChatGPT / Claude の壁打ちログ → `Inbox/{date}/chat-logs/{slug}.md`

置いたら Claude Code に「clippings 集約やって」と言えば、`aggregate-*` skill が Daily に集約します。夜は「EOD distill やって」で Main DB(Work / Others / Research)へ蒸留されます。

> **ここまでで PKM としては完成しています。** Level 1 以降は「手動でやっていることの自動化」です。

---

## Level 1 — + Codex(コード作業の委譲)

コードを書く作業がある人向け。Claude Code は orchestrator に徹し、実装は Codex に委譲する設計です([[CLAUDE.md]] §4)。

1. [Codex CLI](https://github.com/openai/codex) をインストール(ChatGPT サブスクリプションが必要)
2. vault ルートの `AGENTS.md` が Codex 向けの契約として自動で読まれます
3. Claude Code に「この機能を実装して」と頼むと、`codex-consult` skill 経由で Codex に委譲されます

> **Codex を使わない場合**:`.claude/hooks/check-codex-*.py` が Codex 委譲を促す hook として入っています。コード作業をしない、または Claude Code に直接書かせたい場合は、この hook を `.claude/hooks/` から削除して構いません。ノート運用には影響しません。

---

## Level 2 — + Hermes 本体(外部接続の土台)

ここからが「外部ツールとの繋ぎ込み」です。**すべての外部接続(Slack / Google / GitHub / Notion / Genspark)の認証は Hermes が一元所有**します。Claude Code は外部 API を直接叩きません(理由は [[.claude/rules/agent-boundaries.md]] §6 — 認証の重複保有と split-brain を防ぐため)。

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

**一度に全部やらないでください。** 1 本繋いだら動作確認し、数日運用して馴染んでから次に進むのがおすすめです。

接続ごとの手順・動作確認・トラブルシューティングは [`docs/connections/`](./docs/connections/README.md) にあります。

### 推奨順序

| 順 | 接続 | 難易度 | 所要 | 得られるもの | ガイド |
|---|---|---|---|---|---|
| ① | **GitHub** | ★☆☆ | 10分 | コード変化の EOD capture。**PAT 1 本で済むので、Hermes → Inbox パイプライン全体の動作確認に最適** | [docs/connections/github.md](./docs/connections/github.md) |
| ② | **Google Calendar + Tasks** | ★★☆ | 30–60分 | 朝の briefing 自動化(この vault の一番おいしい部分) | [docs/connections/google-calendar-tasks.md](./docs/connections/google-calendar-tasks.md) |
| ③ | **Slack** | ★★★ | 30–60分 | 業務会話の日次ダイジェストが vault に残る | [docs/connections/slack.md](./docs/connections/slack.md) |
| ④+ | Web クリッピング / Genspark 議事録 / Notion | ★★☆ | 各15–30分 | 記事・AI 壁打ち / 会議文字起こし / 清書 publish | [docs/connections/README.md](./docs/connections/README.md) |

④ 以降は完全に任意です。**使わない接続の capture skill(`.hermes/skills/vault-capture/` 配下)は削除して構いません。**

### 接続の状態がわからなくなったら

Claude Code に頼んでください:

```text
接続チェックして
```

`connection-doctor` skill([[.claude/skills/connection-doctor/SKILL.md]])が各接続を診断し、「どこが繋がっていて、どこが切れていて、次に何をすべきか」を表で報告します。

---

## つまずいたら

1. まず「接続チェックして」で切り分け(上記)
2. 各接続ガイドの「よくある躓き」セクションを見る([`docs/connections/`](./docs/connections/README.md))
3. それでも駄目なら、Claude Code にエラーメッセージを貼って相談 — vault の設計を理解した状態で一緒にデバッグしてくれます

## 関連

- [[README.md]] — アーキテクチャ全景
- [[docs/connections/README.md]] — 接続別セットアップガイド
- [[.claude/rules/agent-boundaries.md]] — なぜ外部接続は Hermes 一元所有なのか
- [[.claude/rules/inbox-routing.md]] — capture → Daily → Main DB の流れ
