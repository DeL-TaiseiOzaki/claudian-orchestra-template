# Test Cases

`vault-consistency-check` の検証ケース。各項目は `automated-fixture` か `manual` を明示する。

### 1. Broken wikilinks missing note
- kind: automated-fixture
- setup: touched-today 対象の note に `[[MissingNote]]` を入れる。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06`
- expected output: `- ERROR [Broken wikilinks] ... :: \`[[MissingNote]]\` の参照先が解決できません。提案: 対象ノート名または見出し表記を確認してください（提案のみ・auto-fix なし）。`

### 2. Broken wikilinks missing header
- kind: automated-fixture
- setup: `[[Existing#Missing Header]]` を入れ、ノート本体だけ存在させる。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06`
- expected output: `- ERROR [Broken wikilinks] ... :: \`[[Existing#Missing Header]]\` の見出しが見つかりません。提案: 対象ノート内の見出し表記を確認してください（提案のみ・auto-fix なし）。`

### 3. Frontmatter schema missing client
- kind: automated-fixture
- setup: `Work/PROJ_A/logs/*.md` から `client` を外し、`project: PROJ_A` は残す。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06`
- expected output: `- WARN [Frontmatter schema violation] Work/PROJ_A/logs/... :: frontmatter に不整合があります: \`work field missing: client\`。提案: frontmatter に必須項目と想定 enum を追加・修正してください（提案のみ・auto-fix なし）。`

### 4. Inbox stagnation stale date folder
- kind: automated-fixture
- setup: `Inbox/2026-05-20/clippings/old.md` を作り mtime を 8 日前にする（date-first: 滞留は `Inbox/{YYYY-MM-DD}/` フォルダ単位で測る）。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode full --date 2026-06-06`
- expected output: `- WARN [Inbox stagnation] Inbox/2026-05-20 :: \`Inbox/2026-05-20/\` に 8 日以上未処理のファイルが 1 件あります。提案: Daily ハブへ集約・蒸留するか、不要なら整理してください（提案のみ・auto-fix なし）。`

### 5. Today Tasks drift state mismatch
- kind: automated-fixture
- setup: Daily 側に `- [x] Write report`、Hermes モック JSON 側に `{"title":"Write report","status":"needsAction"}` を返させる。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode full --date 2026-06-06 --enable-remote`
- expected output: `- WARN [Today Tasks drift] Daily/2026-06-06.md :: Daily と Google Tasks の状態に 1 件の差分があります...`

### 6. Code-Map repo health classification
- kind: automated-fixture
- setup: Hermes モック JSON で `live / private_inaccessible / deleted_or_renamed / network_error` を混在させる。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode full --date 2026-06-06 --enable-remote`
- expected output: `- WARN [Code-Map repo health] Maps/Code-Map.md :: \`https://github.com/...\` は \`private_inaccessible\` と判定されました。提案: private 想定なら注記追加、移転済みなら URL を見直してください（提案のみ・auto-fix なし）。`

### 7. Work logs project mismatch
- kind: automated-fixture
- setup: `Work/PROJ_B/logs/foo.md` に `project: PROJ_A` を入れる。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode full --date 2026-06-06`
- expected output: `- WARN [Work logs project field] Work/PROJ_B/logs/foo.md :: \`project\` が \`PROJ_B\` と一致していません...`

### 8. Submodule dirty and pointer drift
- kind: automated-fixture
- setup: `git submodule status --recursive` に `+` と `-` を含め、`git status --porcelain` に `Research` を含める。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode full --date 2026-06-06`
- expected output: `Submodule dirty / commit drift` の `WARN` が少なくとも 2 行出る。

### 9. Idempotent section replacement
- kind: manual
- setup: Daily に既存の `## 🔍 整合性チェック` を 1 個入れておく。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/write_daily_section.py --date 2026-06-06 < section.md`
- expected output: 書き戻し後も `## 🔍 整合性チェック` は 1 個だけで、内容だけ更新される。

### 10. Manual trigger + optional schtasks weekday light
- kind: manual
- setup: SKILL.md の「起動方法」節（manual trigger model ＋オプション schtasks）を確認する。
- command: `rg -n 'manual trigger|--mode light|MON,TUE,WED,THU,FRI' .claude/skills/vault-consistency-check/SKILL.md`
- expected output: `manual trigger`（既定）と、平日 light の schtasks（`--mode light` / `MON,TUE,WED,THU,FRI` / `/st 21:57`）を含む。

### 11. Optional schtasks weekend full
- kind: manual
- setup: SKILL.md の「起動方法」節（オプション schtasks）を確認する。
- command: `rg -n '--mode full|SAT,SUN' .claude/skills/vault-consistency-check/SKILL.md`
- expected output: 週末 full の schtasks（`--mode full` / `SAT,SUN` / `/st 21:57`）を含む。

### 12. Daily missing writer fallback
- kind: automated-fixture
- setup: `Daily/2026-06-06.md` が存在しない状態にする。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/write_daily_section.py --date 2026-06-06 < section.md`
- expected output: stderr に `WARN [Daily missing] Daily/2026-06-06.md`、終了コードは `2`。

### 13. Light performance budget
- kind: manual
- setup: touched-today を 100 files 程度、Hermes 呼び出しは最大 1 回以下の条件で回す。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06`
- expected output: 30 秒以内に完了し、summary 行に `mode: light` を含む。

### 14. Malformed Hermes JSON
- kind: automated-fixture
- setup: Hermes が JSON 以外を返すようモックする。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode full --date 2026-06-06 --enable-remote --json`
- expected output: JSON の `findings` に `{"tag":"WARN","check_name":"Today Tasks drift"...}` または `{"tag":"WARN","check_name":"Code-Map repo health"...}` が残り、run 全体は継続する。

### 15. Structure drift unexpected root dir
- kind: automated-fixture
- setup: vault root 直下に registry 外の dir（例 `Foo/`）を作る。`structure_expected_root_dirs` には含めない。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06`
- expected output: `- WARN [Structure drift] Foo :: vault root 直下に registry 外のディレクトリ \`Foo/\` があります。提案: 想定構造なら schema_rules.yaml の structure_expected_root_dirs に登録、不要なら整理してください（提案のみ・auto-fix なし）。`（`.git` / `.claude` / `.obsidian*` 等の system dir は flag されない）

### 16. Structure drift missing required dir
- kind: automated-fixture
- setup: `Work/PROJ_A/meetings/` を一時的に存在しない状態にする（`structure_required_dirs` には残す。date-first 化で `Work/*/inbox/` は required から除外済み）。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06`
- expected output: `- ERROR [Structure drift] Work/PROJ_A/meetings :: ルールが前提とするディレクトリ \`Work/PROJ_A/meetings/\` が物理的に存在しません。提案: .gitkeep 付きで作成するか、不要なら schema_rules.yaml の structure_required_dirs から外してください（提案のみ・auto-fix なし）。`

### 17. Structure drift non-md placement and empty dir (full only)
- kind: automated-fixture
- setup: `Others/Activities/Conferences/CONF2026/foo.py`（`_assets/` の外）を置き、空 dir `Others/Activities/Foo/`（`.gitkeep` 無し）を用意する。`Inbox/{YYYY-MM-DD}/attachments/` 配下や `*/_assets/` 配下、`Maps/*.base`、`.gitkeep`、`.canvas` は flag されないことも確認する。（空 dir を `Inbox/` 直下に置くと (d) ではなく (b2) Inbox shape で WARN になる→ #19）
- command: `uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode full --date 2026-06-06`
- expected output: `- WARN [Structure drift] Others/Activities/Conferences/CONF2026/foo.py :: ... 想定外の場所にある非 md ファイルです。...` と `- WARN [Structure drift] Others/Activities/Foo :: \`Others/Activities/Foo/\` が空で \`.gitkeep\` がないため git が追跡できません。...`。light mode では (c)/(d) は出ない。

### 18. Wikilink resolution covers non-scan files
- kind: automated-fixture
- setup: scan 対象ノートに `[[README.md]]`（root 直下）、`[[Work/CLAUDE.md]]`、`[[Maps/Home.md]]`、`[[Templates/daily-note.md]]`、`[[Maps/views/logs.base|logs]]` を書く（いずれも実在ファイル。md と非 md（`.base`）の両方をカバー）。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-10`
- expected output: これらのリンクは `Broken wikilinks` として flag されない（resolution index は content-scan の除外（SCAN_EXCLUDED_FILENAMES / NOTE_ROOTS / 非 md）と独立に、`.git` / `.trash` / `.tmp` / `.uv-cache` / `.obsidian*` を除く vault 全 file を索引する）。

### 19. Structure drift Inbox shape (date-first, b2)
- kind: automated-fixture
- setup: `Inbox/oldsource/`（非日付フォルダ）と `Inbox/2026-06-06/unknownsrc/`（未知 source サブフォルダ）を作る。
- command: `uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06`
- expected output: `- WARN [Structure drift] Inbox/oldsource :: \`Inbox/oldsource/\` は Inbox 直下の想定外フォルダです（日付ファースト: \`Inbox/YYYY-MM-DD/\`）。...` と `- WARN [Structure drift] Inbox/2026-06-06/unknownsrc :: \`Inbox/2026-06-06/unknownsrc/\` は未知の source サブフォルダです...`。(b2) は light/full 両方で出る。
