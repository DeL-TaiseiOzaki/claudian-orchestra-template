---
title: "{{date:YYYY-MM-DD}} デイリー"
type: "log"
status: "in-progress"
projects: []
tags: []
created: {{date:YYYY-MM-DD}}
updated: {{date:YYYY-MM-DD}}
---

# {{date:YYYY-MM-DD}} デイリー

## 🌅 朝のbriefing

### 📅 今日の予定
<!-- daily-briefing skill が Inbox/daily（or Calendar）から自動挿入 -->

### 📅 明日の予定
<!-- daily-briefing skill が Inbox/daily（or Calendar）から自動挿入 -->

### ✅ 今日のタスク（Google Tasks）
<!-- 正本は Google Tasks。読み取りの写し。ここで新規タスクを起票しない -->
- [ ] 

### 🎯 Today's Focus
- [ ] 
- [ ] 
- [ ] 

### ⚠️ 注意点・前日からの持ち越し
- 

---

## 🤖 ジョブリスト（on-demand）

<!--
  cron は廃止。ユーザーがこのセクションを見て「○○やって」「全部回して」と指示
  → コアエージェントが hermes に CLI 委譲（[[.claude/skills/hermes-query/SKILL.md]]）または直接実行。
  チェックは daily-briefing が `Inbox/{date}/{source}/...` の存在を見て自動付与（取得済→[x]）。手動チェックも可。
  詳細は [[.claude/rules/daily-operations.md]] §0 / 各 SKILL.md 「起動方法」節。

  各行末尾の `connection:` コメントは [[.claude/connections.yaml]] の registry キー。
  daily-briefing が Daily 生成時に enabled な接続の行だけを残す（未セットアップなら
  「接続セットアップして」= connection-setup の案内を 1 行入れる）。キーなしの行は常に残す。
-->

### 取り込み（capture → `Inbox/{date}/{source}/...`）
- [ ] **Calendar + Tasks**（朝 briefing 用素材）→ `inbox-daily-capture` <!-- connection: google-calendar google-tasks -->
- [ ] **Slack**（今日 ＋ 前日 catch-all）→ `slack-capture` <!-- connection: slack -->
- [ ] **GitHub EOD**（Code-Map 由来 repo の today 変化）→ `github-eod-capture` <!-- connection: github -->
- [ ] **AI 議事録**（今日完了した MTG の transcript を取得。Genspark は `genspark-mtg` で一括／他サービスはエクスポート投入）→ `Inbox/{date}/mtgs/` <!-- connection: meeting-notes -->
- [ ] **RSS 巡回**（購読フィードの新着 → clippings）→ hermes on-demand <!-- connection: rss -->
- [ ] **Web 記事 / AI 壁打ち**（Inbox/{date}/clippings/・chat-logs/ に着地済か確認）→ `clippings-capture`（拡張経由・任意） <!-- connection: web-clippings -->

### 集約（aggregate → `Inbox/{date}/*` から Daily へ append）
- [ ] **朝 briefing**（`Inbox/{date}/daily/daily.md` → root Daily ハブ・予定/タスク/ジョブ状態）→ `daily-briefing`（朝のみ）
- [ ] **Slack 集約**（slack digests → Daily の Work / ミーティング・メモ section）→ `aggregate-slack` <!-- connection: slack -->
- [ ] **MTG 集約**（mtgs/ の transcripts → Daily の Work / ミーティング section に要約 bullet）→ `aggregate-mtgs` <!-- connection: meeting-notes -->
- [ ] **Code 集約**（github-eod code.md → Daily の Work / Research / Others section に per-repo 1-2 行）→ `aggregate-code` <!-- connection: github -->
- [ ] **Clippings 集約**（web 記事 → Daily の Others / 該当 section）→ `aggregate-clippings` <!-- connection: web-clippings -->
- [ ] **Chat logs 集約**（ChatGPT/Claude 会話 → Daily の Others / 該当 section）→ `aggregate-chat-logs` <!-- connection: web-clippings -->

### MTG 準備（pre-meeting → 各 `meetings/` に議事録の叩き台）
- [ ] **MTG 準備**（今日参加する MTG の議事録叩き台作成＋Daily リンク・目的等はヒアリング。Genspark 利用時は bot 準備ガイドも）→ `mtg-prep` <!-- connection: meeting-notes -->

### 配分（distill → Daily から Main DB へ蒸留）
- [ ] **EOD distill**（Daily ログから durable な内容を Work/Others/Research/knowledges/ へ。話者名は [[Maps/People-Map.md]] で名寄せ。raw Inbox は `{area}/sources/` へ）→ `eod-distill`（夜 1 回・直列）
- [ ] **Tasks 反映**（完了・defer 提案 → ユーザー承認 → hermes 反映）→ `hermes-query` <!-- connection: google-tasks -->

### 検査・バックアップ（check / publish）
- [ ] **vault 整合性チェック**（light / full）→ `vault-consistency-check`
- [ ] **GitHub バックアップ**（vault → your-org/your-vault 一方向 push）→ `vault-github-sync`

---

## 📝 ログ（日中の追記）

### 🏢 Work
<!-- 概要のみ。詳細は Work/{XXX}/logs/{{date:YYYY-MM-DD}}.md に書く。触らない案件の行は削除してよい -->
- **PROJ_A**: 
- **PROJ_B**: 
- **PROJ_C**: 
- **PROJ_D**: 
- **PROJ_E**:
- **PROJ_F**: 

### 🔬 Research
- 

### 💡 Others / Insights
- 

### 🗒️ ミーティング・連絡メモ
- 

---

## 🌙 夜の振り返り

### ✅ 完了したこと
- 

### ❌ 未完了 / 持ち越し
- 

### 📤 蒸留・移送先（EOD distill）
<!-- 今日のログ/Inbox から evergreen へ移したものと移送先リンク -->
- 

### 💭 感想・気付き
- 

### 🎯 明日に向けて
- [ ] 
- [ ] 

---

*Created: {{date:YYYY-MM-DD}} | Last Updated: {{date:YYYY-MM-DD}}*
