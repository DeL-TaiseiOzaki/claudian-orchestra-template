# Vault タグ体系

## タグ命名規則

- **小文字** のみ使用
- **ハイフン区切り** （アンダースコア不使用）
- 例：`#data-analysis`, `#model-training`, `#fine-tuning`

---

## Wiki タグ

### テーマ・分野タグ

```
#llm              # Large Language Model
#vlm              # Vision Language Model
#transformer      # Transformer
#attention        # Attention 機構
#fine-tuning      # ファインチューニング
#in-context-learning
#prompt-engineering
#mechanistic-interpretability  # メカニスティック解釈
```

### 実験タイプタグ

```
#ablation-study   # アブレーション研究
#comparison       # 比較実験
#scaling-law      # スケーリング則
#benchmark        # ベンチマーク
```

### リソース・効率タグ

```
#gpu-intensive    # GPU集約的
#cpu-friendly     # CPU対応
#low-resource     # 低リソース
#reproducible     # 再現可能
```

### 状態タグ

```
#to-read          # 読む予定
#key-paper        # 重要な論文
#preliminary      # 予備的
#confirmed        # 確認済み
#seed             # 未検証の着想
#exploring        # 仮説を探索中
```

### ノート種別・成果物タグ

`type` が分類の正本だが、横断検索を補助するときに使う。

```
#exploration      # 仮説検証・PoC
#experiment       # 実験記録
#code             # コード関連
#codebase         # コードベース読解
```

### 進行管理タグ

```
#meeting          # ミーティング
#documentation    # ドキュメント
#urgent           # 急ぎ
#blocker          # ブロッカー
#in-review        # レビュー待ち
```

### 活動タグ

```
#activity         # 継続的活動の記録（type: note と併用）
#community        # コミュニティ・委員・WG
```

### 個人学習・スキルアップ

```
#learning         # 学習
#tutorial         # チュートリアル
#book-note        # 書籍ノート
#skill-building   # スキルビル
```

### 管理・ライフ

```
#todo             # やることリスト
#health           # 健康
#finance          # 財務
#idea             # アイデア帳
```

### Vault 運用・テンプレート

```
#moc              # Map of Content / domain 入口
#weekly-review    # 週次レビュー
#documentation    # ドキュメント更新
#setup            # セットアップ手順
#onboarding       # 初回導入
#connections      # 外部接続
#capture          # raw capture
#archive          # Archive 入口・運用
#inbox            # Inbox 入口・運用
```

外部 provider 名（`github`、`slack`、`zotero` など）や knowledge note の category / tool tag は、英小文字・ハイフン区切りの命名規則を守る限り追加してよい。provider 固有 tag を pipeline の必須判定には使わない。

---

## タグの使用例

### Wiki ノート例（文献）
```markdown
tags: ["llm", "fine-tuning", "in-context-learning", "key-paper", "to-read"]
```

### Daily ログ例
```markdown
tags: ["llm", "learning", "meeting"]
```

---

## タグの階層化（オプション）

Obsidian では `tag/subtag` の形式で階層化できます：

```
#wiki/llm/fine-tuning
#wiki/vlm/vision-encoder
```

ただし、シンプルさを優先する場合は**フラット構造**を推奨します。

## 関連

- [[.codex/rules/vault-metadata.md]]（frontmatter スキーマの単一の正）
- [[.codex/rules/language.md]] / [[.codex/rules/wiki-management.md]]
