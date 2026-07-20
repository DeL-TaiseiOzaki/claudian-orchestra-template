# AGENTS.md — Claudian Orchestra コア契約

**この Obsidian vault は個人知識基盤**であり、**2 つのエージェント**で運用する。

| エージェント | 役割 | 既定 |
|---|---|---|
| **コアエージェント** | 対話、オーケストレーション、実装、curated note の編集すべて | **Codex**（Codex CLI） |
| **Hermes** | 常駐 ingestion。Slack / Google / GitHub MCP など、認証を伴う外部接続を一元所有 | [Hermes Agent](https://github.com/NousResearch/Hermes-Agent)（任意） |

このファイルが**唯一のコア契約**である。Codex はこのファイルを直接読み、従う。

---

## 0. コア構成と用語

コアエージェントは **Codex CLI** 単体である。rules / skills / registry / docs を含む control plane の正本はすべて `.codex/` 配下に置く。Codex は `AGENTS.md`（このファイルと各ドメイン直下の nested `AGENTS.md`）を直接読み、`.codex/skills/{name}/SKILL.md` を参照して skill を実行する。

同時に動くコアは**必ず 1 つ**である。旧来の二頭体制（Claude が指揮し、Codex が委譲実装する形）は廃止した。現在のコアエージェントが判断と実装の両方を担う。

---

## 1. ドメイン構成

| ドメイン | パス | 内容 |
|---|---|---|
| **Inbox** | `Inbox/{YYYY-MM-DD}/{daily,slack,discord,code,mtgs,clippings,chat-logs,mail,attachments}/` | raw で未整理の capture 専用受信域。**日付ファースト**。Hermes と capture extension だけが新規 capture を作成できる。**auto-route はしない**。コアとユーザーは Inbox に直接書かず、コアが同日分を Daily へ集約した後に curate する。[[Inbox/README.md]] |
| **Daily** | `Daily/` | 1 日につき 1 つのハブであり、**人間の監査面**でもある。job-list の状態、wikilink 付き集約 bullet、distill 提案と配分先、整合性チェック結果など、すべてのエージェント操作を追跡できる形で残す。`Inbox/{date}/*` を集約し、Main DB へ配分する。 |
| **Wiki** | `Wiki/` | 唯一の Main DB。アイデア、学習・読書ノート、文献・実験ノート、活動・プロジェクト記録、会議要約を置く。[[.codex/rules/wiki-management.md]] |
| **Maps** | `Maps/` | 横断 MOC と Bases view。コードベース知識の入口は `Code-Map.md`。 |
| **Persona** | `Persona/` | 著者プロフィールの単一の正。 |
| **Meta** | `Meta/` | vault 自身についてのすべて。自己言及プロジェクト、接続別の setup / verification / troubleshooting（`Meta/connections/`）、リポジトリ asset（`Meta/assets/`）を置く。distill の配分先にはしない。入口は [[GETTING-STARTED.md]]。 |
| **Archive** | `Archive/` | 非活性コンテンツの退避先。削除せず `status: archived` にする。 |
| **Templates** | `Templates/` | ノートテンプレート。 |

> Wiki と Persona は、直下の `AGENTS.md` に固有契約を持つ。Codex は nested `AGENTS.md` を自動で読み込む。

## 2. ノート操作の原則（最優先）

- ノートは Markdown で管理する。Markdown 以外の作業成果物は `_assets/`、外部の one-shot resource は immutable な `sources/` に置く。
- 新規フォルダ、rename、move などの構造変更は、対応する rules / README の更新と同じ commit に含める。
- ノートには必ず frontmatter（`type` / `status` / `tags` / `created` / `updated`）を付ける。path 固有 override を含む schema は [[.codex/rules/vault-metadata.md]]、tag は [[.codex/rules/vault-tagging.md]] に従う。
- domain rule は [[.codex/rules/wiki-management.md]] / [[.codex/rules/daily-operations.md]] に従う。
- Hermes / コアの capture-curate 分離と single-writer は [[.codex/rules/agent-boundaries.md]] に従う。
- Obsidian 方言（wikilink、embed、callout、Bases）を維持し、不要な reflow はしない。

## 3. 言語規約

- **思考、内部処理、commit message、identifier、frontmatter の key / enum value、tag**：英語。
- **ユーザーへの応答**：既定は日本語。ユーザーの言語に合わせて調整してよい。
- 詳細は [[.codex/rules/language.md]]。

## 4. 運用モデル — 1 コア、on-demand 既定

コアエージェントは、対話、判断、設計、実装を一貫して担う。実装専用の別チャットエージェントへ委譲する前提はない。

- **認証を伴う外部接続は Hermes が一元所有する**。push は capture → `Inbox/{date}/{source}/`、pull は `hermes chat -q`（[[.codex/skills/hermes-query/SKILL.md]]）で行う。コアは外部 OAuth / PAT を保持しない。例外は [[.codex/rules/agent-boundaries.md]] §6 の vault 自身の local `git` / `gh`、Web research の read、ならびに認証を Hermes と共有しない capture extension である。
- **on-demand が既定**。Daily の `## 🤖 ジョブリスト` を運用 checklist とし、ユーザーの「○○やって」を受けてコアが実行または Hermes へ委譲する。既存 cron は過渡期に限って維持できるが、新規登録はしない。[[.codex/rules/daily-operations.md]] §0。
- **Daily が監査面**。capture、aggregate、distill、check のすべてについて、着地先、提案、承認結果を Daily から追えるようにする。Daily から記録を削除しない。
- **Skill** の正本は `.codex/skills/{name}/SKILL.md`。Codex は標準配置から直接 discovery する。
- 大規模な調査・分析は、コア CLI の parallel / sub-agent 機構を使ってよい。結果は `.codex/docs/research/` または `.codex/docs/libraries/` に置く。
- delete、複数ファイルの rename、schema migration、外部 write、Main DB への配分など、破壊的または戻しにくい操作はユーザー承認を得る。tier は [[.codex/rules/agent-boundaries.md]] §5 に従う。

### 出力契約

- 結論 → 根拠 → 次のアクションの順で伝える。不確実性は guess / unverified / needs-check として明示する。
- 実行した command、変更した file、test 結果を必ず示す。失敗は原因と影響範囲を添え、隠さない。

### 最終応答前の quality gate

- ユーザーの意図と実装が一致していることを確認する。
- diff を自己レビューする。
- 実行可能な check を最低 1 つ走らせる。

## 5. 書き込み境界（single-writer 原則）

| パス | 書き手 |
|---|---|
| `Inbox/{YYYY-MM-DD}/**` | Hermes と capture extension だけが**新規 capture**を作成できる。コアとユーザーは直接書かない。Daily 集約前に限り Hermes は同じ capture job を idempotent に再実行できる。Daily に集約した時点で、その source file の所有権はコア + ユーザーへ移り、Hermes は以後更新しない。 |
| `Daily/**`, `Wiki/**`, `Maps/**`, `Persona/**`, `Templates/**` | コアエージェント + ユーザー |
| `.codex/**`（rules / skills / registry / docs を含む control plane） | コアエージェント + ユーザー |
| `.hermes/**` の `SKILL.md` / references / config | Hermes 自身には read-only。観測結果は `Inbox/{date}/clippings/` に残す。コア + ユーザーは編集可。 |
| 外部 code repository | Hermes の GitHub MCP 経由では **read-only**。変更は各 repository の PR flow で行う。 |

- auto-committer は同時に 1 つだけ動かす。cloud sync、Obsidian Git、Hermes と競合させない。
- vault の GitHub backup は local `git` / `gh` を使う。[[.codex/skills/vault-github-sync/SKILL.md]]。

## 6. コア（Codex）の注意

- model、reasoning effort、approval、sandbox、Web access は user-level Codex settings で管理する。テンプレートでは固定しない。
- sandbox が書き込みを許可していても、§5 の境界を守る。
- `claude.ai` connector（Google Drive read など）は使えない。Hermes 経路を使う。[[Meta/connections/google-drive.md]] 経路 B。
- Codex 固有の discovery は [[.codex/AGENTS.md]] を参照する。

## 7. リポジトリ規約

- repository 管理下の **Python** command と依存管理には `uv` を使い、`python` / `pip` を直接呼ばない。Hermes の Google helper だけは、Hermes が導入した package と token を再利用するため、明示的に解決した `HERMES_RUNTIME_PY` を使う限定例外とする。依存の追加には引き続き `uv` を使う。
- `.codex/rules/` はこのファイルより優先する。矛盾を見つけた場合は黙って選ばず、明示する。
- 調査 artifact は `.codex/docs/research/` または `.codex/docs/libraries/` に、簡潔かつ日付付きで置き、元タスクから link する。

## 関連

- [[README.md]] — architecture overview
- [[GETTING-STARTED.md]] — 段階的セットアップ
- [[.codex/skills/connection-setup/SKILL.md]] — 接続 wizard
- [[.codex/rules/agent-boundaries.md]] — Hermes / コアの分担
