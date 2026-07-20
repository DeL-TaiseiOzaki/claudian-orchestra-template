# Codex コア補足

ルートの `AGENTS.md` が完全な運用契約です。このファイルには Codex 固有の discovery 補足だけを記載します。

- ルール、skills、registry、運用 knowledge の正本は `.codex/` 配下（`.codex/rules/` `.codex/skills/` `.codex/connections.yaml` `.codex/docs/`）に置きます。
- Codex は repository skills を `.codex/skills/{name}/SKILL.md` から検出します。
- project の `.codex/config.toml` は最小構成を維持します。model、reasoning、approval、sandbox、web の設定は利用者が決めます。
- 認証を伴う外部サービスは `.codex/rules/agent-boundaries.md` の定義どおり Hermes が所有します。
