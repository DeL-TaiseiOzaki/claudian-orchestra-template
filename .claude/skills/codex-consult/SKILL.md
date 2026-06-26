---
name: codex-consult
description: Consult Codex for code design, planning, complex implementation (>10 LOC), debugging / root-cause analysis, trade-off comparisons, and code review. Use BEFORE writing non-trivial code, when facing an architecture or design decision, when stuck on a bug, when comparing implementation approaches, or after substantial code changes. Code work only — note (.md) editing is handled directly and never goes to Codex.
---

# Codex Consultation Skill

Claude Code は **オーケストレーター**。コードの設計・計画・複雑な実装・デバッグ・レビューは
**Codex に相談**して結果を統合する（自分で大規模実装しない）。このスキルは「いつ・どう相談し・
どう統合するか」の手順書。判定基準は `CLAUDE.md` §3/§4 と `.claude/hooks/check-codex-*.py` と一致。

## 1. When to consult Codex (triggers)

次のいずれかに当てはまったら相談する：

| トリガー | 例 |
|----------|----|
| 実装が **10 LOC 超** になりそう | 新規関数群・クラス・モジュール追加 |
| **2ファイル以上**を編集 / **3ファイル以上**を読む必要 | 横断的リファクタ・依存追跡 |
| **設計判断・トレードオフ比較**が要る | 「A案 vs B案」「この構造でよいか」 |
| **デバッグ / 根本原因分析** | 「なぜ落ちる？」再現条件が不明 |
| **テスト戦略**の立案 | カバレッジ方針・境界値設計 |
| **コードレビュー**（実装後） | hook 目安: ≥3ファイル or ≥100行の変更 |
| Web/最新情報の検証が必要 | ライブラリ最新仕様（→ research は general-purpose） |

### Do NOT consult Codex for

- **ノート（`.md`）の作成・編集** → Claude が直接行う（Vault の本来業務）。
- **単一ファイルの軽微な修正（10 LOC 以下）** → Claude が直接行う。
- これらに Codex を挟むのは過剰。`CLAUDE.md` の Non-Goals / ノート運用原則に従う。

## 2. How to consult — two modes

### Mode A（既定）: general-purpose サブエージェント経由【コンテキスト保全】

実体のある作業（計画立案・設計比較・実装・レビュー）は **Task → `subagent_type='general-purpose'`** に委譲する。
サブエージェント（Opus）が内部で `codex exec` を呼び、**要約だけ**を返すのでメイン文脈を消費しない。
3つの hook が薦める既定経路もこれ。

委譲プロンプトに必ず含める：
1. **目的（Goal）** — 何を達成したいか
2. **制約（Constraints）** — 既存規約・`.claude/rules/`・互換性・環境（`uv` など）
3. **対象（Context）** — 関連ファイルのパス、現状の方針、エラーログ要点
4. **問い（Ask）** — Codex に何を判断/生成してほしいか
5. **戻り形式** — §3 の構造で要約して返すよう指示

### Mode B: 直接 `codex exec`【軽い読み取り質問のみ】

即答が欲しい read-only の小さな質問なら、Claude から直接呼んでよい（`Bash(codex:*)` は許可済み）：

```bash
# 分析・レビュー（読み取り専用）
codex exec --model "${CODEX_MODEL:-gpt-5.5}" --sandbox read-only "<question>"

# 実装（ファイル書き込み可。多くは Mode A 経由を推奨）
codex exec --model "${CODEX_MODEL:-gpt-5.5}" --sandbox workspace-write "<task>"
```

> [!note] sandbox の選択
> 分析・設計比較・レビュー = `read-only`。実際にコードを書かせる時のみ `workspace-write`。

## 3. Response format to request from Codex

Codex は `AGENTS.md` の規定により次の構造で返す。相談時もこの構造での回答を明示的に求める：

```markdown
## TL;DR            # 結論 3行以内
## Analysis         # 問題分解・前提・制約
## Plan             # 実装ステップ
## Patch Strategy   # どのファイルを何のために変更するか
## Validation       # 実行すべきテスト/検証コマンド
## Risks            # 失敗時の影響と緩和策
```

## 4. Consultation templates

### Plan（計画立案）
> Goal: <feature>. Constraints: <rules/env>. Context: <paths>. 依存・順序・リスクを含む実装計画を、TL;DR/Analysis/Plan/Patch Strategy/Validation/Risks の構造で。

### Design decision（設計判断・比較）
> 問題: <X>。案A=<...> / 案B=<...>。採用案とその理由、却下理由、移行コストを比較して。read-only。

### Debug / root-cause（根本原因）
> 症状: <error>。再現条件: <...>。関連ファイル: <paths>。ログ要点: <...>。根本原因の仮説と検証手順を優先度順に。

### Code review（レビュー）
> 変更概要: <...>。`git diff` の対象: <files>。正確性・境界条件・互換性・テスト容易性の観点でレビューし、重大度付きで指摘して。read-only。

### Implementation（実装）
> Plan: <承認済み計画>。最小diffで実装し、テストも添えて。workspace-write。完了後 Patch Strategy/Validation を要約。

## 5. Integrate the result（結果の統合）

Codex / サブエージェントの返答を受けたら、`CLAUDE.md` §6/§7 に従う：

1. **自己レビュー** — 返ってきた diff / 計画を鵜呑みにせず点検（意図一致・blast radius）。
2. **検証** — 最低1つの実行可能なテスト/チェックを通す（無ければ何を確認すべきか明記）。
3. **ユーザー報告** — 結論 → 根拠 → 次アクションの順。実行コマンド・変更ファイル・テスト結果を提示。
4. **不確実性の明示** — 推測 / 未検証 / 要確認 を区別する。
5. **言語** — ユーザー向け説明は日本語、コード・識別子・コマンドは英語（`.claude/rules/language.md`）。

## 6. Relationship to enforcement hooks

これらの hook が「相談すべき瞬間」を自動でリマインドする（**ブロックはしない**）：

| Hook | 発火 | 役割 |
|------|------|------|
| `check-codex-before-write.py` | コード Write/Edit 前（設計指標検出時） | 相談の促し |
| `check-codex-after-plan.py` | 計画系 Task 後 | 計画レビューの促し |
| `post-implementation-review.py` | コード ≥3ファイル / ≥100行 | レビューの促し |

hook が促してきたら、このスキルの Mode A で相談を実行する。hook はコードファイル限定で、
ノート（`.md`）編集には介入しない。

## 関連

- [[CLAUDE.md]] §3 Routing / §4 Delegation Trigger / §5 Execution Patterns / §6 Output Contract
- [[.codex/AGENTS.md]]（Codex 側の応答契約）
- [[.claude/agents/general-purpose.md]]（委譲先サブエージェント定義）
- [[.claude/rules/language.md]]
