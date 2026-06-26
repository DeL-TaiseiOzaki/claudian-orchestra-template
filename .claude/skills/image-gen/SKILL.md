---
name: image-gen
description: Generate images via Codex CLI's built-in `$imagegen` skill (gpt-image-2, with gpt-image-1.5 fallback) and place them into the vault. Use when the user asks to create / generate an image, icon, banner, thumbnail, or illustration for a note (画像/アイコン/バナー/サムネ/挿絵を作って). Codex generates the PNG to its LOCAL dir because its sandbox cannot write the Drive-mounted vault; Claude then copies the file into the target note's `_assets/` and embeds it with `![[...]]`. Requires `codex login` (ChatGPT auth — no API key). NOT for reading/analyzing existing images (use Read) or for diagrams that Mermaid / Canvas can cover (use json-canvas).
---

# Image Generation Skill — Codex `$imagegen` 経由

ユーザーの画像生成要求を **Codex CLI の組み込み `$imagegen`**（gpt-image-2）に委譲し、
生成された PNG を **Claude が vault の `_assets/` に配置**して `![[...]]` 埋め込みまで行う手順書。
判定・委譲方針は `CLAUDE.md` §4 と整合（外部生成＝Codex、vault への書き込み＝Claude）。

## 0. アーキテクチャ（なぜ「Codex 生成 → Claude コピー」なのか）

スモークテスト（2026-06-16）で確認した制約に基づく：

| 役割 | 担い手 | 理由 |
|------|--------|------|
| 画像**生成** | Codex（`$imagegen`） | 組み込み skill。auth は `codex login`（ChatGPT・APIキー不要） |
| vault への**配置**（`cp`）+ 埋め込み | **Claude** | Codex の `workspace-write` サンドボックスは **Google Drive マウント（vault `<vault root>` on a remote-mounted drive）に書けない**（`Access to the path is denied`）。生成物は必ずローカル `~/.codex/generated_images/<session>/ig_*.png` に出るので、Claude が Bash で vault にコピーする |

- **Codex に vault パスへの保存を頼まない**（できないし、`Inbox/**` 等は vault ルールで拒否される）。Codex は「生成だけ」させ、Claude が後段を担う。
- auth 前提：`codex login status` が `Logged in using ChatGPT` であること（未ログインなら `codex login`）。

## 1. When to use / not use

**Use**：「画像 / アイコン / バナー / サムネ / 挿絵 / ロゴ案 を作って」「この記事の図を生成して」等。

**Do NOT use**：
- 既存画像の読み取り・分析 → `Read`（画像を視覚的に読む）
- フローチャート・マインドマップ・関係図で済む → `json-canvas` / Mermaid
- 厳密な図表・スクショ加工 → 画像生成は不向き

## 2. 集める入力

| 入力 | 必須 | 既定 / 備考 |
|------|------|------------|
| description（英語推奨・具体的に） | ✅ | スタイル・被写体・配色・背景を明示すると安定 |
| 対象ノート（配置先 `_assets/` を決める） | 推奨 | `<current_note>` があればそのフォルダ。無ければユーザーに確認 |
| size（`WIDTHxHEIGHT`） | 任意 | 既定 `1024x1024`。16 の倍数・縦横比 1:3〜3:1・最大 3840x2160（4K はβ・2K 生成→外部アップスケール推奨） |
| count | 任意 | 既定 1。複数なら順次生成 |
| 入力画像（編集 / 参照） | 任意 | `codex exec -i <path.png>`（PNG/JPEG） |

## 3. 手順

### Step A — 保存先とファイル名を決める
- 配置先は **対象ノートのフォルダ直下 `_assets/`**（既定方針）。例：ノートが `Work/PROJ_A/project.md` なら `Work/PROJ_A/_assets/`。
- 対象ノートが不明なら**ユーザーに確認**（勝手に `Inbox/` には置かない＝capture 専用領域）。
- `slug` は description から英小文字ハイフンで作る。filename = `<slug>.png`（衝突時は `-2`, `-3`）。

```bash
ASSETS="<target-note-folder>/_assets"        # 例: Work/PROJ_A/_assets
mkdir -p "$ASSETS"
```

### Step B — 生成を Codex に委譲（stdout は読まない・background 実行）
Codex の出力は vault context を echo して**約 80k トークン**になるため、**stdout を context に読み込まない**。
ログはファイルに捨て、生成物はファイルシステムから検出する（Step C）。

```bash
# 生成前のスナップショット（新規ファイル検出用）
BEFORE=$(ls -t ~/.codex/generated_images/*/*.png 2>/dev/null | head -1)

codex exec -s workspace-write --skip-git-repo-check \
  '$imagegen <DESCRIPTION>. Target size <WxH>. IMPORTANT: gpt-image-2 frequently returns "at capacity" — if so, fall back to gpt-image-1.5. Generating is enough; do not attempt to save into the project tree.' \
  > /tmp/imagegen-$$.log 2>&1
```

- **Bash tool では `run_in_background: true` で実行**（生成は 30 秒〜数分）。完了通知を待ってから Step C。
- `$imagegen` はシングルクォートで渡す（`$` がシェル変数展開されないように）。
- **フォールバック指示は必須**：gpt-image-2 の容量エラーは頻発する。明示すると gpt-image-1.5 で突破できる。

### Step C — 生成物を検出（Codex の stdout に依存しない）
```bash
NEW=$(ls -t ~/.codex/generated_images/*/*.png 2>/dev/null | head -1)
```
- `NEW` が空、または `NEW == BEFORE`（新規ファイル無し）→ **生成失敗**（多くは容量エラー）。
  - 対処：少し時間をおいて Step B を再試行。連続失敗なら `tail -5 /tmp/imagegen-$$.log` で原因確認しユーザー報告。

### Step D — Claude が vault にコピー
```bash
cp "$NEW" "$ASSETS/<slug>.png"
file "$ASSETS/<slug>.png"      # PNG であることを確認
```

### Step E — 対象ノートに埋め込み
- ファイル名が vault 内で一意なら `![[<slug>.png]]`、曖昧なら vault ルート相対の `![[<target-note-folder>/_assets/<slug>.png]]`。
- 適切なセクション（または末尾）に Edit で追記。

### Step F — 検証・後片付け
- `Read` で目視確認（任意だが推奨）。
- Codex のセッションdir掃除（任意）：`rm -rf "$(dirname "$NEW")"`。`/tmp/imagegen-$$.log` も削除可。

## 4. Gotchas（スモークテスト 2026-06-16 で実証）

- **Drive マウント書込不可** → 必ず Claude が `cp`。Codex に vault パス保存をさせない。
- **`Selected model is at capacity`** が頻発 → プロンプトで **gpt-image-1.5 フォールバックを必ず指示**。失敗時は時間をおいて再試行。
- **透過（transparency）非対応**（gpt-image-2 は `background=transparent` 不可）→ 必要なら gpt-image-1.5 を明示するか後処理（chroma-key）。
- **コスト**：画像ターンはテキストの **3〜5 倍** の Codex 利用枠を消費。レート上限あり（標準 250/分、新規アカウント 5/分）。乱発しない。
- **context 節約**：Codex の冗長 stdout を会話に流さない（ログはファイルへ、検出はファイルシステムで）。
- **`codex login` 必須**：ChatGPT 認証。`OPENAI_API_KEY` を設定すれば API 経路（API 課金・大量バッチ向け）も可だが、既定は組み込み経路。

## 5. Output contract（ユーザー報告）

結論 → 根拠 → 次アクションの順で、以下を必ず示す：
- 生成画像の vault パス（`![[...]]` 埋め込み込み）
- 埋め込み先ノート
- 使用モデル（gpt-image-2 / gpt-image-1.5）とサイズ
- 失敗・フォールバックがあればその旨

## 関連

- [[.claude/skills/codex-consult/SKILL.md]]（Codex 委譲の一般手順。本 skill は画像生成特化）
- [[CLAUDE.md]] §4 Routing（画像生成＝Codex 委譲、vault 書込＝Claude）
- [[.claude/rules/language.md]]（応答は日本語、コマンド・識別子は英語）
- [[.claude/rules/vault-metadata.md]]（`_assets/` ＝非 md 作業物の置き場）
