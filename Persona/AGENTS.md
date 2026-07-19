# AGENTS.md — Persona（著者プロフィールの単一の正）

vault 全体から参照される **identity SoT**（single source of truth）。
Wiki の提案・活動・応募ノートが、ここの内容を再利用する。

## 構成（推奨）

`Persona/` 配下にプロフィールを Markdown で分割して置く：

```
Persona/
├── README.md          # 入口（誰か、現在の役割）
├── bio.md             # 経歴（学歴 / 職歴）
├── publications.md    # 論文・記事・発表
├── skills.md          # 専門スキル
├── projects.md        # 主な案件・OSS・活動
└── _assets/           # 顔写真などの非 md
```

## 使い方

- frontmatter `resource:` で他ノートから明示的に参照可（例：`resource: Persona/bio.md`）
- 個別ノートで自己紹介を書くときは、ここからの**抜粋**にとどめ、原文の二重管理を避ける

## 注意

- 公開する vault では本フォルダの粒度を慎重に調整する（個人情報を漏らさない）
- public template（このリポ）には**実プロフィールを入れない**。各利用者が自分の内容で埋める

## やってはいけない

- 各案件・活動ノート内に self-bio を散在させる（必ずここから参照する）
- 古いバージョンを別ファイルで残す（履歴は git に任せる）
