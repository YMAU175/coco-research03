# ココナラ カテゴリランキング スクレイピングツール

ココナラ（coconala.com）のカテゴリ別ランキングTOP10のサービス情報を自動収集するPythonツールです。

## 機能

- カテゴリページからランキングTOP10を正確に取得
- 各サービスの詳細情報を抽出
- 30日以内のレビュー数を高精度で検出
- CSV形式でデータを出力

## 収集データ

各サービスから以下の情報を収集します：

- ランキング順位
- サービス名
- 評価点（5点満点）
- 説明文の文字数
- FAQの有無
- トークルーム回答例の有無
- 直近30日のレビュー数
- 価格
- 総レビュー数
- サービスURL

## インストール

### 必要環境

- Python 3.8以上
- pip

### セットアップ

```bash
# リポジトリをクローン
git clone [repository-url]
cd coco-research03

# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化
source venv/bin/activate  # Mac/Linux
# または
venv\Scripts\activate  # Windows

# 必要なライブラリのインストール
pip install requests beautifulsoup4 pandas
```

## 使い方

### 基本的な使用方法

```bash
# 仮想環境を有効化
source venv/bin/activate

# 1カテゴリをスクレイピング（デフォルト）
python coconala_scraper_fixed.py

# 複数カテゴリをスクレイピング
python coconala_scraper_fixed.py --categories 3

# リクエスト間隔を調整（デフォルト: 2秒）
python coconala_scraper_fixed.py --delay 3.0

# 出力ファイル名を指定
python coconala_scraper_fixed.py --output my_results.csv
```

### コマンドラインオプション

- `--categories`: 処理するカテゴリ数（デフォルト: 1）
- `--delay`: リクエスト間隔（秒）（デフォルト: 2.0）
- `--output`: 出力ファイル名（デフォルト: coconala_ranking_fixed.csv）

### 特定カテゴリの直接指定

```python
from coconala_scraper_fixed import CoconalaScraperFixed

# スクレイパーのインスタンス作成
scraper = CoconalaScraperFixed(delay=2.0)

# カテゴリ情報を定義
category_info = {
    'category_name': '文字起こし・データ入力',
    'url': 'https://coconala.com/categories/429',
    'main_category_id': 429,
    'category_level': 1
}

# スクレイピング実行
results = scraper.scrape_category_ranking(category_info)
```

## 出力形式

結果は`output/`フォルダにCSV形式で保存されます。

### ファイル名形式
```
output/YYYYMMDD_HHMMSS_coconala_ranking_fixed.csv
```

### CSV列構成
- ranking: ランキング順位
- category_name: カテゴリ名
- service_name: サービス名
- rating: 評価点
- description_length: 説明文の文字数
- has_faq: FAQ有無（True/False）
- has_sample_conversation: トークルーム回答例有無（True/False）
- recent_30_days_reviews: 30日以内のレビュー数
- price: 価格
- total_reviews: 総レビュー数
- service_url: サービスURL
- category_url: カテゴリURL

## プロジェクト構成

```
coco-research03/
├── coconala_scraper_fixed.py  # メインスクリプト（最終版）
├── category_urls.csv          # カテゴリ一覧データ
├── output/                    # 結果CSV出力フォルダ
├── docs/                      # プロジェクト仕様書
│   ├── やりたいこと.md
│   ├── 技術検証.md
│   └── 全体設計.md
├── CLAUDE.md                  # AI実行時の指示書
├── README.md                  # このファイル
└── venv/                      # Python仮想環境
```

## 技術仕様

### 30日レビュー数の検出ロジック

本ツールは以下の高精度アルゴリズムで30日以内のレビューを検出します：

1. 「評価・感想」セクションから日付情報を抽出
2. 厳密な重複除去（同じ日付は1件のみカウント）
3. 相対日付（○日前）と絶対日付（○月○日）の両方に対応

### レート制限対策

- デフォルトで2秒間隔のリクエスト
- User-Agentヘッダーの適切な設定
- エラー時の適切なハンドリング

## 注意事項

### 法的・倫理的配慮

- ウェブサイトの利用規約を遵守してください
- robots.txtの内容を確認してください
- サーバーに負荷をかけないよう、適切な間隔でアクセスしてください
- 収集したデータは個人的な分析目的でのみ使用してください

### 技術的制限

- JavaScriptで動的に読み込まれるコンテンツは取得できません
- ログインが必要な情報は取得できません
- 「もっと見る」ボタンで展開される追加コンテンツは取得対象外です

## トラブルシューティング

### ModuleNotFoundError

```bash
# 仮想環境が有効化されているか確認
which python3
# venv/bin/python3 と表示されればOK

# ライブラリを再インストール
pip install -r requirements.txt
```

### 取得件数が少ない

- ページの構造が変更された可能性があります
- `--delay`オプションで間隔を長くしてみてください

## ライセンス

本プロジェクトは研究・学習目的で作成されています。
商用利用の際は、ココナラの利用規約をご確認ください。

## 更新履歴

- 2024.06.29: 初版リリース
  - 30日レビュー数の高精度検出機能を実装
  - ランキング順での正確な取得を実現
  - 重複除去アルゴリズムの最適化