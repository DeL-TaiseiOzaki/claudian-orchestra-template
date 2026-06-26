---
name: genspark-slide
description: Hermes-side skill that kicks a Genspark slide-generation task via `gsk task slides`. Returns task_id / Genspark URL / optional local PPTX path on stdout for the caller. Does NOT write any vault notes — Claude orchestrates the call via `hermes chat -q -s genspark-slide` and writes the reference note (under Work/{XXX}/deliverables/ or similar) using the returned metadata. Trigger when the user asks for slide / deck generation tied to a meeting, topic, or set of source materials.
version: 1.0.0
author: your-org
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vault, genspark, slides, external-api, mymemory]
    related_skills: [genspark-mtg]
---

# genspark-slide

Genspark の `gsk task slides` を起動するだけの **Hermes 側 thin wrapper**。

> **役割境界（2026-06-16 整理 / 2026-06-16 hermes 移管）**：
> - 旧 Claude 側 [[Archive/.claude/skills/genspark-slide/SKILL.md]] は外部接続を持っていたため、**外部接続=Hermes 原則**（[[.claude/rules/agent-boundaries.md]] §6）に従い本スキルへ移管。
> - **本スキルは task を kick して結果メタデータを stdout で返すだけ**（vault には書き込まない）。
> - **Vault のリファレンスノート作成は Claude の責務**（呼び出し元）。Claude は `hermes chat -q -s genspark-slide` で本スキルを叩き、返ってきた `task_id` / URL / PPTX path を `Work/{XXX}/deliverables/{topic}.md` 等に手で書く。
> - 議事録取得は [[.hermes/skills/mymemory/genspark-mtg/SKILL.md]]、Calendar 取得は [[.hermes/skills/mymemory/inbox-daily-capture/SKILL.md]]（兄弟スキル）。

---

## 前提

### インストール

```bash
npm install -g @genspark/cli   # Node.js >= 18
gsk --version
```

### 認証

| 方式 | コマンド / 環境変数                       | 用途         |
| -- | -------------------------------- | ---------- |
| 環境変数 | `GSK_API_KEY="gsk_..."`         | Hermes 既定（headless） |
| 対話 | `gsk login` → ブラウザで OAuth        | 初回認証       |
| 確認 | `gsk me`                         | ログイン状態確認   |

設定ファイル：`~/.genspark-tool-cli/config.json`。Hermes は `GSK_API_KEY` を `.hermes/.env` 経由で持つ前提（[[.claude/rules/agent-boundaries.md]] §6 — 外部認証は hermes 一元集約）。

### バージョン確認

`gsk` のサブコマンドは更新が速い．**実装前に必ず help を引いてスキーマを確認**する：

```bash
gsk task --help
gsk task slides --help
```

---

## トリガー

| Claude 側の指示例 | 本スキルが行う操作 |
| --- | --- |
| 「この会議内容で 10 枚のスライドを作って」 | §1 slides 起動（task_id / URL を返す） |
| 「{資料} を元にプレゼン生成」 | §1 slides 起動 |
| 「`{task_id}` の slides 結果を PPTX で取って」 | §2 export（PPTX をローカル保存し path を返す） |

Claude → Hermes 委譲フォーマット：

```powershell
$env:PYTHONUTF8 = '1'
Set-Location "<vault root>"

hermes chat -q "Load genspark-slide and run `gsk task slides --task_name '{topic}' --query '...' --instructions '...' -o '{topic}.pptx'`. Return task_id, Genspark URL, and the local PPTX path on stdout as a small JSON object." -s genspark-slide -Q --source claude-code
```

---

## §1. スライド生成

### 起動（task 作成）

```bash
gsk task slides \
  --task_name "{topic}" \
  --query "{何のスライドか自然文で。末尾で slides を生成することを明示}" \
  --instructions "{追加指示。言語・トーン・構成・枚数・スタイル}"
```

`gsk` v1.0.23 で `slides` は `task` / `create_task` の task type。`--query` 必須、`--task_name` と `--instructions` 推奨。

### PPTX export

```bash
gsk task slides \
  --task_name "{topic}" \
  --query "{材料と目的。presentation slides を生成することを明示}" \
  --instructions "日本語、business-formal、10枚、図解多め" \
  -o "./{topic}.pptx"
```

- `-o` の export 形式は task type から自動判定（slides は pptx 想定）。
- export 不可の場合は task 自体は走るが、CLI が `Warning: Export not available` / `Warning: Export failed` を出すことあり。

### 入力ファイルを渡す

- ローカルファイルなら `gsk upload <file>` で `file_wrapper_url` を取得し、その URL を `--query` または `--instructions` に明示的に埋め込む。
- `gsk task --file <values...>` も可（CSV/Excel 向け説明だが他形式でも動く可能性）。PDF/Markdown/Word は `gsk upload` → URL 明記が安全。

### 言語・トーンの既定（Claude が指定しない場合のデフォルト）

- 言語：日本語（business-formal）
- 構成：表紙 → アジェンダ → 本文 (5–8 枚) → まとめ → Next Actions
- 図表：データがあれば積極的に使う

---

## §2. 返却データの形式

stdout に小さな JSON を返す（Claude が parse して vault note 作成に使う）：

```json
{
  "task_id": "tsk_xxxxxxxx",
  "task_name": "{topic}",
  "genspark_url": "https://www.genspark.ai/agents?type=task&id=tsk_xxxxxxxx",
  "pptx_path": "./{topic}.pptx",   // -o を渡したときだけ
  "warnings": ["Export not available"]  // あれば
}
```

stdout は他の log を混ぜない（Claude が `JSON.parse` する前提）。log は stderr へ。

---

## §3. Hermes が **しない** こと

- **Vault への書き込み**（curated path も Inbox も）。task 完了通知ノートを Inbox に書く運用は議論の余地ありだが、現状は **stdout return のみ**。
- **要約・タグ推論・本文編集**（task 起動 paramater は Claude から渡された raw を使う）。
- **session-log / Daily 更新**（呼び出し側の Claude セッション内で `session-log` skill を使う）。

---

## §4. エラー・落とし穴

| 症状                       | 対処 |
| ------------------------ | ----- |
| `gsk` が PATH に無い         | `.hermes/.env` で path を補完するか、`PATH` を gateway service に渡す |
| 認証は通るが 403 / 401          | プランが Free のままで CLI 機能が制限されている可能性。`gsk me` で plan 確認 |
| サブコマンドの引数が help と違う      | `gsk <cmd> --help` を再取得 |
| PPTX が CLI 経由で落とせない      | `gsk drive` / `gsk download` 経由、または Web UI から手動 export（Plus プラン前提のことあり） |
| Windows cron で `gsk` shim 解決失敗 | Windows `.cmd` shim を直接呼ぶ（`C:/Users/.../hermes/node/gsk.cmd ...`）。詳細：[[.hermes/skills/mymemory/genspark-mtg/SKILL.md]] の同種注意 |

---

## §5. 不確実な点

1. `gsk task slides` の出力受け取り（PPTX / PDF の CLI 取得経路）は完全には未検証。`gsk drive download` 経由が有力。
2. 公式ソースリポジトリは非公開（npm 発行のみ）。スキーマの最終的な正は **`gsk <cmd> --help`** の出力。
3. Free プランでの CLI 機能制限は未検証。
4. 本スキル `genspark-slide` の Hermes 移管後、`-o` 指定の PPTX path は Hermes プロセスの CWD 相対になる。Claude から呼ぶ場合は絶対 path 指定推奨。

実機検証で挙動が確定したら本ファイルを更新する（Cross-territory observation 規約：[[.hermes/skills/mymemory/genspark-mtg/SKILL.md]] と同じ — drift は `Inbox/{date}/clippings/hermes-obs-genspark-slide.md` に observation note）。

---

## 関連

- npm: [@genspark/cli](https://www.npmjs.com/package/@genspark/cli)
- [Genspark AI Slides ヘルプ](https://www.genspark.ai/helpcenter/ai-slides)
- [[.hermes/skills/mymemory/genspark-mtg/SKILL.md]]（議事録 capture・hermes 兄弟スキル）
- [[.hermes/skills/mymemory/inbox-daily-capture/SKILL.md]]（Calendar 全体 capture）
- [[.claude/skills/hermes-query/SKILL.md]]（Claude → Hermes 委譲経路）
- [[.claude/rules/agent-boundaries.md]] §6 接続所有
- [[.claude/rules/vault-metadata.md]]
- [[Templates/work-meeting-note.md]]
