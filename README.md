# カブクリ 公式サイト（Stripe / PayPay 審査対応）

山梨在宅リハビリクリニックが提供するマンジャロ専門オンライン診療「カブクリ」の公式サイト。
Stripe の PayPay capability 審査要件（特商法表記・代表者名・商品価格の掲載・ログイン不要の決済動線）を満たすために作成。GitHub Pages で公開する。

## 構成

| ファイル | 内容 |
|---------|------|
| `index.html` | トップ（サービス紹介・料金表・診療の流れ・注意事項） |
| `payment.html` | お支払いページ（商品選択 → Stripe Payment Link へ遷移。全38商品の動線あり） |
| `tokushoho.html` | 特定商取引法に基づく表記（代表者：鈴木 隆宏）。全ページのフッターからリンク |
| `assets/products.js` | 商品マスタ（価格の単一の正。料金表・支払ページ両方がここから描画） |
| `assets/payment-links.js` | lookup_key → Payment Link URL のマッピング（自動生成、手編集禁止） |
| `scripts/create_payment_links.py` | Stripe に Payment Links を一括作成し `payment-links.js` を生成 |

## PayPay 審査チェックリストとの対応

1. **Stripe登録サイトと同一** → Stripeダッシュボードの事業ウェブサイトURLを本サイトのURLに更新すること（現登録: https://kabukuri.jp）
2. **代表者名の特商法記載** → `tokushoho.html` に「代表者 鈴木 隆宏」を記載
3. **特商法ページへのフッターリンク** → 全3ページのフッターに設置
4. **商品・価格掲載＋ログイン不要で決済画面へ** → `payment.html` から全商品が Stripe Payment Link（会員登録不要）に直行

## デプロイ手順

```bash
# 1. Payment Links を本番モードで生成（要ネットワーク・Stripe本番キー）
python3 scripts/create_payment_links.py --live

# 2. GitHub リポジトリ作成・push（初回のみ）
gh repo create zoen-tech/kabukuri-clinic --public --source . --push

# 3. GitHub Pages 有効化（初回のみ、main / root）
gh api -X POST repos/zoen-tech/kabukuri-clinic/pages \
  -f 'source[branch]=main' -f 'source[path]=/'
```

公開URL: https://zoen-tech.github.io/kabukuri-clinic/

## 価格変更時のルール

- 価格の正は `repo_kabukuri/medical/pricing/pricing-table.md`。変更時は `assets/products.js` と Stripe カタログ（lookup_key 単位）を同時に更新し、`create_payment_links.py` を再実行すること
- 紹介初回割引（`*_ref`）は本サイト非掲載（公開価格は通常価格のみ）

## 注意

- 全ページ `noindex, nofollow`（審査用途のため検索流入は受けない）
- 患者個人情報は一切置かないこと
