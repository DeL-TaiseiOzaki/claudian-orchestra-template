---
name: genspark-slide
description: Start a Genspark slide task and return its task ID, URL, and optional PPTX path to the core agent without writing vault notes.
version: 1.0.0
author: your-org
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vault, genspark, slides, external-api, vault-capture]
    related_skills: [genspark-mtg]
---

# genspark-slide

Genspark の `gsk task slides` を起動するだけの **Hermes 側 thin wrapper**。

> **役割境界（2026-06-16 整理 / 2026-06-16 hermes 移管）**：
> - **本スキルは task を kick して結果メタデータを stdout で返すだけ**（vault には書き込まない）。
> - Vault のリファレンスノート作成はコアエージェントの責務。コアは `hermes chat -q -s genspark-slide` で呼び出し、返された metadata を curated note に記録する。
> - 議事録取得は [[.hermes/skills/vault-capture/genspark-mtg/SKILL.md]]、Calendar 取得は [[.hermes/skills/vault-capture/inbox-daily-capture/SKILL.md]]（兄弟スキル）。

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

設定ファイル：`~/.genspark-tool-cli/config.json`。Hermes は `GSK_API_KEY` を `.hermes/.env` 経由で持つ前提（[[.codex/rules/agent-boundaries.md]] §6 — 外部認証は hermes 一元集約）。

### バージョン確認

`gsk` のサブコマンドは更新が速い．**実装前に必ず help を引いてスキーマを確認**する：

```bash
gsk task --help
gsk task slides --help
```

---

## トリガー

| コア側の指示例 | 本スキルが行う操作 |
| --- | --- |
| 「この会議内容で 10 枚のスライドを作って」 | §1 slides 起動（task_id / URL を返す） |
| 「{資料} を元にプレゼン生成」 | §1 slides 起動 |
| 「`{task_id}` の slides 結果を PPTX で取って」 | §2 export（PPTX をローカル保存し path を返す） |

Core → Hermes 委譲フォーマット：

```bash
# 日本語 Windows のみ PYTHONUTF8=1 を前置（cp932 デコード起因の出力欠落防止）
cd "<vault root>"

hermes chat -q "Load genspark-slide and run `gsk task slides --task_name '{topic}' --query '...' --instructions '...' -o '{topic}.pptx'`. Return task_id, Genspark URL, and the local PPTX path on stdout as a small JSON object." -s genspark-slide -Q --source core-agent
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

### 言語・トーンの既定（コアエージェントが指定しない場合のデフォルト）

- 言語：日本語（business-formal）
- 構成：表紙 → アジェンダ → 本文 (5–8 枚) → まとめ → Next Actions
- 図表：データがあれば積極的に使う

---

## §2. 返却データの形式

stdout に小さな JSON を返す（コアエージェントが parse して vault note 作成に使う）：

```json
{
  "task_id": "tsk_xxxxxxxx",
  "task_name": "{topic}",
  "genspark_url": "https://www.genspark.ai/agents?type=task&id=tsk_xxxxxxxx",
  "pptx_path": "./{topic}.pptx",   // -o を渡したときだけ
  "warnings": ["Export not available"]  // あれば
}
```

stdout は他の log を混ぜない（コアエージェントが `JSON.parse` する前提）。log は stderr へ。

---

## §3. Hermes が **しない** こと

- **Vault への書き込み**（curated path も Inbox も）。task 完了通知ノートを Inbox に書く運用は議論の余地ありだが、現状は **stdout return のみ**。
- **要約・タグ推論・本文編集**（task 起動 parameter はコアから渡された raw を使う）。
- **session-log / Daily 更新**（呼び出し側の コアセッション内で `session-log` skill を使う）。

---

## §4. エラー・落とし穴

| 症状                       | 対処 |
| ------------------------ | ----- |
| `gsk` が PATH に無い         | `.hermes/.env` で path を補完するか、`PATH` を gateway service に渡す |
| 認証は通るが 403 / 401          | プランが Free のままで CLI 機能が制限されている可能性。`gsk me` で plan 確認 |
| サブコマンドの引数が help と違う      | `gsk <cmd> --help` を再取得 |
| PPTX が CLI 経由で落とせない      | `gsk drive` / `gsk download` 経由、または Web UI から手動 export（Plus プラン前提のことあり） |
| Windows cron で `gsk` shim 解決失敗 | Windows `.cmd` shim を直接呼ぶ（`C:/Users/.../hermes/node/gsk.cmd ...`）。詳細：[[.hermes/skills/vault-capture/genspark-mtg/SKILL.md]] の同種注意 |

---

## §5. 不確実な点

1. `gsk task slides` の出力受け取り（PPTX / PDF の CLI 取得経路）は完全には未検証。`gsk drive download` 経由が有力。
2. 公式ソースリポジトリは非公開（npm 発行のみ）。スキーマの最終的な正は **`gsk <cmd> --help`** の出力。
3. Free プランでの CLI 機能制限は未検証。
4. `-o` 指定の PPTX path は Hermes process の CWD 相対になる。コアから呼ぶ場合は absolute path を推奨。

実機検証で挙動が確定したら本ファイルを更新する（Cross-territory observation 規約：[[.hermes/skills/vault-capture/genspark-mtg/SKILL.md]] と同じ — drift は `Inbox/{date}/clippings/hermes-obs-genspark-slide.md` に observation note）。

---

## 関連

- npm: [@genspark/cli](https://www.npmjs.com/package/@genspark/cli)
- [Genspark AI Slides ヘルプ](https://www.genspark.ai/helpcenter/ai-slides)
- [[.hermes/skills/vault-capture/genspark-mtg/SKILL.md]]（議事録 capture・hermes 兄弟スキル）
- [[.hermes/skills/vault-capture/inbox-daily-capture/SKILL.md]]（Calendar 全体 capture）
- [[.codex/skills/hermes-query/SKILL.md]]（Core → Hermes 委譲経路）
- [[.codex/rules/agent-boundaries.md]] §6 接続所有
- [[.codex/rules/vault-metadata.md]]
- [[Templates/meeting-note.md]]
