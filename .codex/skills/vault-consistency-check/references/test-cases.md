# Test Cases

`vault-consistency-check` の検証ケース。各項目は `automated-fixture` か `manual` を明示する。

### 1. Broken wikilinks missing note
- kind: automated-fixture
- setup: touched-today 対象の note に `[[MissingNote]]` を入れる。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06`
- expected output: `- ERROR [Broken wikilinks] ... :: \`[[MissingNote]]\` の参照先が解決できません。提案: 対象ノート名または見出し表記を確認してください（提案のみ・auto-fix なし）。`

### 2. Broken wikilinks missing header
- kind: automated-fixture
- setup: `[[Existing#Missing Header]]` を入れ、ノート本体だけ存在させる。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06`
- expected output: `- ERROR [Broken wikilinks] ... :: \`[[Existing#Missing Header]]\` の見出しが見つかりません。提案: 対象ノート内の見出し表記を確認してください（提案のみ・auto-fix なし）。`

### 2.1 Wikilinks in code are ignored
- kind: automated-fixture
- setup: touched-today 対象の note に inline code `` `[[MissingInlineExample]]` `` と fenced code 内の `[[MissingFenceExample]]` を入れる。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06`
- expected output: code 内の 2 件は `Broken wikilinks` に出ない。通常本文の wikilink は従来どおり検査される。

### 3. Frontmatter schema missing status
- kind: automated-fixture
- setup: touched-today 対象の `Wiki/*.md` から `status` を外す。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06`
- expected output: `- WARN [Frontmatter schema violation] Wiki/... :: frontmatter に不整合があります: \`required field missing: status\`。提案: frontmatter に必須項目と想定 enum を追加・修正してください（提案のみ・auto-fix なし）。`

### 4. Inbox stagnation stale date folder
- kind: automated-fixture
- setup: `Inbox/2026-05-20/clippings/old.md` を作り mtime を 8 日前にする（date-first: 滞留は `Inbox/{YYYY-MM-DD}/` フォルダ単位で測る）。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode full --date 2026-06-06`
- expected output: `- WARN [Inbox stagnation] Inbox/2026-05-20 :: \`Inbox/2026-05-20/\` に 8 日以上未処理のファイルが 1 件あります。提案: Daily ハブへ集約・蒸留するか、不要なら整理してください（提案のみ・auto-fix なし）。`

### 5. Today Tasks drift state mismatch
- kind: automated-fixture
- setup: Daily 側に `- [x] Write report`、Hermes モック JSON 側に `{"title":"Write report","status":"needsAction"}` を返させる。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode full --date 2026-06-06 --enable-remote`
- expected output: `- WARN [Today Tasks drift] Daily/2026-06-06.md :: Daily と Google Tasks の状態に 1 件の差分があります...`

### 6. Code-Map repo health classification
- kind: automated-fixture
- setup: Hermes モック JSON で `live / private_inaccessible / deleted_or_renamed / network_error` を混在させる。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode full --date 2026-06-06 --enable-remote`
- expected output: `- WARN [Code-Map repo health] Maps/Code-Map.md :: \`https://github.com/...\` は \`private_inaccessible\` と判定されました。提案: private 想定なら注記追加、移転済みなら URL を見直してください（提案のみ・auto-fix なし）。`

### 7. Submodule dirty and pointer drift
- kind: automated-fixture
- setup: `git submodule status --recursive` に `+` と `-` を含め、`git status --porcelain` に `.gitmodules` 登録済み submodule path を含める。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode full --date 2026-06-06`
- expected output: `Submodule dirty / commit drift` の `WARN` が少なくとも 2 行出る。

### 8. Idempotent section replacement
- kind: manual
- setup: Daily に既存の `## 🔍 整合性チェック` を 1 個入れておく。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/write_daily_section.py --date 2026-06-06 < section.md`
- expected output: 書き戻し後も `## 🔍 整合性チェック` は 1 個だけで、内容だけ更新される。直後に別の `##` 見出しがある場合は空行を 1 行保ち、見出し同士を連結しない。

### 9. Manual trigger is the default
- kind: manual
- setup: SKILL.md の「起動方法」節を確認する。
- command: `rg -n 'manual trigger|既定（手動 trigger）|--mode light' .codex/skills/vault-consistency-check/SKILL.md`
- expected output: manual trigger が既定で、light の手動 command を含む。

### 10. No new scheduler registration
- kind: manual
- setup: SKILL.md の「既存 scheduled task の扱い」を確認する。
- command: scheduler の新規作成 command が無く、「新規作成・変更はせず」と記載されていることを検索する。
- expected output: 既存 legacy job の過渡期維持と on-demand への移行だけを案内する。

### 11. Daily missing writer fallback
- kind: automated-fixture
- setup: `Daily/2026-06-06.md` が存在しない状態にする。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/write_daily_section.py --date 2026-06-06 < section.md`
- expected output: stderr に `WARN [Daily missing] Daily/2026-06-06.md`、終了コードは `2`。

### 12. Light performance budget
- kind: manual
- setup: touched-today を 100 files 程度、Hermes 呼び出しは最大 1 回以下の条件で回す。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06`
- expected output: 30 秒以内に完了し、summary 行に `mode: light` を含む。

### 13. Malformed Hermes JSON
- kind: automated-fixture
- setup: Hermes が JSON 以外を返すようモックする。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode full --date 2026-06-06 --enable-remote --json`
- expected output: JSON の `findings` に `{"tag":"WARN","check_name":"Today Tasks drift"...}` または `{"tag":"WARN","check_name":"Code-Map repo health"...}` が残り、run 全体は継続する。

### 14. Structure drift unexpected root dir
- kind: automated-fixture
- setup: vault root 直下に registry 外の dir（例 `Foo/`）を作る。`structure_expected_root_dirs` には含めない。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06`
- expected output: `- WARN [Structure drift] Foo :: vault root 直下に registry 外のディレクトリ \`Foo/\` があります。提案: 想定構造なら schema_rules.json の structure_expected_root_dirs に登録、不要なら整理してください（提案のみ・auto-fix なし）。`（`.git` / `.codex` / `.claude` / `.obsidian*` 等の system dir は flag されない）

### 15. Structure drift missing required dir
- kind: automated-fixture
- setup: `Maps/views/` を一時的に存在しない状態にする（`structure_required_dirs` には残す）。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06`
- expected output: `- ERROR [Structure drift] Maps/views :: ルールが前提とするディレクトリ \`Maps/views/\` が物理的に存在しません。提案: .gitkeep 付きで作成するか、不要なら schema_rules.json の structure_required_dirs から外してください（提案のみ・auto-fix なし）。`

### Automated regression suite

- kind: automated-unittest
- command: `uv run python -m unittest discover -s .codex/skills/vault-consistency-check/tests -v`
- coverage: JSON schema SSOT、BOM、quoted/unquoted scalar/list、Templates/knowledge scan、date-first raw capture、`Wiki/sources/**`、source-first Inbox rejection、`Meta/assets/**`。

### 16. Structure drift non-md placement and empty dir (full only)
- kind: automated-fixture
- setup: `Wiki/CONF2026/foo.py`（`_assets/` の外）を置き、空 dir `Wiki/Foo/`（`.gitkeep` 無し）を用意する。`Inbox/{YYYY-MM-DD}/attachments/` 配下や `*/_assets/` 配下、`Maps/*.base`、`.gitkeep`、`.canvas` は flag されないことも確認する。（空 dir を `Inbox/` 直下に置くと (d) ではなく (b2) Inbox shape で WARN になる→ #18）
- command: `uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode full --date 2026-06-06`
- expected output: `- WARN [Structure drift] Wiki/CONF2026/foo.py :: ... 想定外の場所にある非 md ファイルです。...` と `- WARN [Structure drift] Wiki/Foo :: \`Wiki/Foo/\` が空で \`.gitkeep\` がないため git が追跡できません。...`。light mode では (c)/(d) は出ない。

### 17. Wikilink resolution covers non-scan files
- kind: automated-fixture
- setup: scan 対象ノートに `[[README.md]]`（root 直下）、`[[Wiki/AGENTS.md]]`、`[[Maps/Home.md]]`、`[[Templates/daily-note.md]]`、`[[Maps/views/logs.base|logs]]` を書く（いずれも実在ファイル。md と非 md（`.base`）の両方をカバー）。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-10`
- expected output: これらのリンクは `Broken wikilinks` として flag されない（resolution index は content-scan の除外（SCAN_EXCLUDED_FILENAMES / NOTE_ROOTS / 非 md）と独立に、`.git` / `.trash` / `.tmp` / `.uv-cache` / `.obsidian*` を除く vault 全 file を索引する）。

### 18. Structure drift Inbox shape (date-first, b2)
- kind: automated-fixture
- setup: `Inbox/oldsource/`（非日付フォルダ）と `Inbox/2026-06-06/unknownsrc/`（未知 source サブフォルダ）を作る。
- command: `uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06`
- expected output: `- WARN [Structure drift] Inbox/oldsource :: \`Inbox/oldsource/\` は Inbox 直下の想定外フォルダです（日付ファースト: \`Inbox/YYYY-MM-DD/\`）。...` と `- WARN [Structure drift] Inbox/2026-06-06/unknownsrc :: \`Inbox/2026-06-06/unknownsrc/\` は未知の source サブフォルダです...`。(b2) は light/full 両方で出る。
