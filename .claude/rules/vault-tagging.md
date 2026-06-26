# Vault タグ体系

## タグ命名規則

- **小文字** のみ使用
- **ハイフン区切り** （アンダースコア不使用）
- 例：`#data-analysis`, `#model-training`, `#fine-tuning`

---

## Work タグ

### プロジェクトタグ（例）

実案件のコードに合わせて差し替える：

```
#proj-a              # Client A
#proj-b              # Client B
#proj-c              # Client C
#proj-x              # Client X (archived / lost)
```

### フェーズ・ステータスタグ

```
#proposal         # 提案（受注前：サーベイ→提案→見積）
#requirements     # 要件定義
#design           # 設計
#development      # 開発
#validation       # 検証
#deployment       # デプロイ
#maintenance      # 保守
```

### タスクタイプタグ

```
#data-preparation # データ前処理
#model-training   # モデル学習
#evaluation       # 評価
#bug-fix          # バグ修正
#documentation    # ドキュメント
#meeting          # ミーティング
#client-feedback  # クライアント対応
```

### 優先度・進捗タグ

```
#urgent           # 急ぎ
#blocker          # ブロッカー
#in-review        # レビュー待ち
#ready-for-deploy # デプロイ準備完了
```

---

## Research タグ

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
```

---

## Others タグ

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

---

## タグの使用例

### Work ノート例
```markdown
tags: ["proj-a", "model-training", "data-preparation", "in-review"]
```

### Research ノート例
```markdown
tags: ["llm", "fine-tuning", "in-context-learning", "key-paper", "to-read"]
```

### Daily ログ例
```markdown
tags: ["proj-a", "proj-b", "model-training", "meeting"]
```

---

## タグの階層化（オプション）

Obsidian では `tag/subtag` の形式で階層化できます：

```
#work/data-prep
#work/model-training
#research/llm/fine-tuning
#research/vlm/vision-encoder
```

ただし、シンプルさを優先する場合は**フラット構造**を推奨します。

## 関連

- [[.claude/rules/vault-metadata.md]]（frontmatter スキーマの単一の正）
- [[.claude/rules/language.md]] / [[.claude/rules/work-management.md]] / [[.claude/rules/research-management.md]] / [[.claude/rules/others-management.md]]
