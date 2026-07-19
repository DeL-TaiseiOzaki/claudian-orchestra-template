---
name: connection-setup
description: Interactive onboarding wizard for external connections. Use when the user says 「セットアップして」「接続セットアップ」「初期設定」「どのツールを繋ぐか選びたい」, when GETTING-STARTED Level 3 is reached, or when connection-doctor finds everything unconfigured. Interviews the user by USE CASE (not tool name) to decide which of the catalog connections (GitHub / Google Calendar / Google Tasks / Gmail / Google Drive / Slack / Discord / RSS / web clippings / AI meeting notes / Zotero / Notion) they actually use, records the selection in .claude/connections.yaml, then walks through setup of ONLY the selected ones — one connection at a time, following docs/connections/{guide}.md, verifying each before moving on. Non-catalog tools get the alternatives table (docs/connections/README.md); non-Gmail mail is unified by forwarding to Gmail. Re-runnable: also used to add or drop a connection later.
---

# connection-setup — 対話式・接続セットアップウィザード

このテンプレートの利用者が**自分の使うツールを選び、選んだものだけ**を確実に繋ぐためのウィザード。
「全部繋ごうとして挫折する」「使わないツールの手順で迷子になる」を防ぐのが目的。

## 原則

- **ユースケースで聞く**:「slack-capture を有効にしますか?」ではなく「業務の会話は Slack で進みますか?」と聞く。利用者はツール名や skill 名を知らない前提
- **1 問ずつ**:質問はまとめて長文で投げず、対話で 1 つずつ。選択式で答えられる形にする(質問ツールが使える環境では選択肢 UI を使う)
- **選ばなかったものは視界から消す**:`.claude/connections.yaml` に `disabled` を記録 → ジョブリスト(daily-briefing)と診断(connection-doctor)から自動的に外れる
- **1 本ずつ・検証してから次へ**:選択された接続は推奨順に 1 本ずつセットアップし、動作確認が通ってから次に進む。途中でやめても再実行で続きから再開できる(registry の `unconfigured` / `enabled` を見る)
- **secrets は会話に貼らせない**:トークン・URL は `.hermes/.env` 等に置いてもらい、「設定した」の報告だけ受ける

## Step 0: 現状把握

1. `.claude/connections.yaml` を読む(無ければテンプレ初期状態で作成)
2. 全て `unconfigured` → 初回セットアップとして Step 1 から
3. 一部 `enabled` / `disabled` → 「前回の続き」か「構成変更」かを確認して該当 Step へ
4. 環境チェック(軽く):`hermes --version` の成否だけ確認。**まだ無くても質問は進める**(必要になった時点で [[GETTING-STARTED.md]] Level 2 に誘導)

## Step 1: ヒアリング(ユースケース → 接続の対応)

以下を 1 問ずつ聞く。カッコ内が対応する registry キー:

| # | 質問(例) | Yes の場合 | 補足 |
|---|---|---|---|
| 1 | 仕事や活動の**会話は Slack** で進みますか? | `slack` | Teams 等 → カタログ外(下記) |
| 2 | **コミュニティや研究グループの会話は Discord** ですか? | `discord` | **bot を入れられるサーバのみ**(self-bot は規約違反)。skill は slack-capture をひな形に生成 |
| 3 | **予定は Google カレンダー**で管理していますか? | `google-calendar` | ics 経路なら 10 分・OAuth 不要 |
| 4 | **ToDo は Google Tasks** で管理していますか? | `google-tasks` | Calendar と同じ capture に相乗り(OAuth 必要)。Todoist 等 → カタログ外 |
| 5 | **メールを vault から検索・参照**したいですか? | `gmail` | Gmail 以外(Outlook / 会社メール)の場合は「**Gmail への自動転送で一本化**」を案内(個別接続は作らない) |
| 6 | チームや客先との**資料共有は Google Drive / Docs** ですか? | `google-drive` | read 専用。claude.ai コネクタなら Hermes 不要 |
| 7 | **コードを書きますか?** リポジトリは GitHub にありますか? | `github` | 書かない人は不要 |
| 8 | **ブログやニュースの定期購読(RSS)**を vault に流し込みたいですか? | `rss` | 認証不要・最も手軽 |
| 9 | **Web 記事や AI チャット(ChatGPT/Claude)のログ**を貯めたいですか? | `web-clippings` | Hermes 不要の経路あり |
| 10 | 会議で **AI 文字起こし**を使っていますか?(Genspark / Otter / tl;dv / Notta 等) | `meeting-notes` | Genspark は自動アダプタ同梱、他サービスはエクスポート投入(どれでも乗る) |
| 11 | **文献管理は Zotero** ですか?(研究者) | `zotero` | pull 参照 + 文献ノート起票 |
| 12 | 清書を **Notion で共有**する必要がありますか? | `notion` | 個人利用のみなら不要 |

> Google 系(3〜6)は同じ OAuth 基盤に乗るので、いずれか 1 つでも OAuth 経路を通せば残りは「GCP で API を有効化 → 必要なら再認可」だけで足せる。質問時にその旨を添えると心理的負担が下がる。

- 「わからない」→ その接続は `unconfigured` のまま残す(後で足せることを伝える)
- **全部 No でも問題ない**ことを明言する(Level 0 の手動運用で PKB として完成している)

**カタログ外ツール**(Teams / Todoist / Linear / Jira / Readwise 等)を使っていると答えた場合:
- [[docs/connections/README.md]] の「カタログ外ツールの対応方針」対応表を案内する
- 代替 2 択を提示:(a) 当面は手動で `Inbox/{date}/{source}/` に置く運用、(b) 自作 capture skill を作る(「{ツール名} 用の capture skill を設計して」と頼めば、既存 skill(§関連)をひな形に Claude+Codex で設計できる。着地先は必ず `Inbox/{date}/` 配下・capture only の原則に従う)

## Step 2: 選択を registry に記録

- Yes → `status: enabled`、No → `status: disabled`、わからない → `unconfigured` のまま
- `.claude/connections.yaml` を更新し、選択結果の一覧表を提示して確認を取る
- 以後、daily-briefing のジョブリストと connection-doctor はこの registry を読んで動く

## Step 3: 選ばれた接続を 1 本ずつセットアップ

**推奨順**:`github`(最短・パイプライン体感)→ `google-calendar` + `google-tasks`(価値最大)→ `gmail` / `google-drive`(同じ OAuth 基盤のついでに)・`rss`(認証不要)→ `slack` / `discord` → 残り(`meeting-notes` / `zotero` / `notion`)。
ただし `requires_hermes: false` のもの(`web-clippings` / `google-drive` コネクタ経路 / `meeting-notes` 手動経路)は Hermes 未導入でも先にできる。

各接続について:

1. **Hermes 前提の確認**:`requires_hermes: true` で Hermes 未導入なら、先に [[GETTING-STARTED.md]] Level 2 を一緒に済ませる
2. 対応するガイド(registry の `guide`)を読み、**手順を 1 ステップずつ提示**する。ブラウザでの操作(PAT 作成・OAuth 同意・Slack app 作成)はユーザーにやってもらい、完了報告を待つ
3. ガイドの**動作確認**(pull → push)を実行し、`Inbox/{date}/{source}/` への着地まで確認する
4. 通ったら次の接続へ。失敗したらガイドの「よくある躓き」表で切り分け(必要なら [[.claude/skills/connection-doctor/SKILL.md]] の該当チェックを単発実行)
5. 1 本終わるごとに「ここで一旦止めて、数日運用してから次を足す」選択肢を提示する(全部を今日やる必要はない)

## Step 4: 使わない接続の後始末(任意・承認必須)

`disabled` にした接続について:

- **既定は registry で無効化するだけ**(ジョブリスト・診断から消える。skill ファイルは残る=いつでも復活可)
- ユーザーが望む場合のみ、対応する capture skill ディレクトリ(registry の `capture_skill`)の**削除を提案 → 承認後に実行**(不可逆操作は承認前提・[[.claude/rules/agent-boundaries.md]] §5)

## Step 5: 完了サマリ

1. [[.claude/skills/connection-doctor/SKILL.md]] を実行して最終状態の表を出す
2. 「明日の朝、Daily を作るとジョブリストには選んだ接続だけが並ぶ」ことを伝える
3. 次アクション(残りの `unconfigured`、数日後に足す候補)を 1–2 行で提示

## 再実行(構成変更)

- 「Slack も繋ぎたくなった」→ 該当接続だけ Step 3 を実行し registry を `enabled` に
- 「Genspark やめた」→ registry を `disabled` に(+Step 4 の後始末を提案)

## 関連

- [[.claude/connections.yaml]] — 選択の記録先(single source of truth)
- [[docs/connections/README.md]] — 接続別ガイド(Step 3 の台本)
- [[.claude/skills/connection-doctor/SKILL.md]] — 診断(Step 3 の検証・Step 5)
- [[.claude/skills/daily-briefing/SKILL.md]] — ジョブリストが registry を反映する側
- [[GETTING-STARTED.md]] — Level 0〜3 の全体導線
- 自作 capture skill のひな形:[[.hermes/skills/vault-capture/README.md]] と各 SKILL.md(capture-only・Inbox 着地・冪等性の原則)
