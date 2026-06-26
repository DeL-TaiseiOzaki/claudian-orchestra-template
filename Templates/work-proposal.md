---
title: "[PROJECT_CODE] [提案タイトル]"
project: "PROJECT_CODE"
type: "note"
status: "draft"
client: "クライアント名"
proposal_type: "proposal"   # proposal | estimate | scope | other
# resource: "Work/PROJECT_CODE/sources/<filename>"  # optional · 根拠となる先方資料 / サーベイへのポインタ（OKF 整合）
tags: ["project_code", "proposal"]
created: {{DATE:YYYY-MM-DD}}
updated: {{DATE:YYYY-MM-DD}}
---

# [PROJECT_CODE] [提案タイトル]

> 案件の**提案フェーズ成果物**（`Work/{案件}/proposals/`・**受注前**）。提案書・スライド骨子・概算見積・スコープ・体制など。
> 受注後の定常ドキュメントは `docs/`、納品物は `deliverables/` へ（受注前 / 受注後の境界を保つ）。失注時は `status: archived`（削除しない）。

## 🎯 提案骨子（ひとことで）

- 

## 🧩 背景・課題（先方の困りごと）

- 

## 🛠️ 技術アプローチ

- 
- 根拠サーベイ：`Work/PROJECT_CODE/references/`

## 📐 スコープ・体制

### 含む / 含まない
- 含む：
- 含まない：

### 体制・役割
- 

## 💰 概算見積

| 項目 | 内容 | 概算 |
|------|------|------|
|  |  |  |

## ✅ 次アクション / 提案ステータス

- [ ] 
- ステータス：提案中（受注 → `status.md` の「全体フェーズ」を**デリバリ**へ更新。失注 → `status: archived`）

## 🔗 参照

- [[Work/PROJECT_CODE/project.md]] / [[Work/PROJECT_CODE/status.md]]
- 関連MTG：`Work/PROJECT_CODE/meetings/` ／ サーベイ：`Work/PROJECT_CODE/references/`
