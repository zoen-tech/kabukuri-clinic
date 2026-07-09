#!/usr/bin/env python3
"""カブクリ審査用サイトの Stripe Payment Links を一括作成し、
assets/payment-links.js を生成する。

- 対象: マンジャロ通常価格 36 SKU + オプション 2 商品（計38リンク）
  ※紹介初回割引はサイト非掲載のため対象外
- 商品・価格が Stripe 側に無ければ作成する（repo_kabukuri/finance/stripe/create_catalog.py と同一データ・同一lookup_key）
- 既に同じ lookup_key の有効な Payment Link がある場合は再利用（metadata で判定）

使い方（ターミナルで実行）:
  python3 scripts/create_payment_links.py           # テストモード
  python3 scripts/create_payment_links.py --live    # 本番モード（PayPay審査用はこちら）

鍵は ~/.config/stripe/config.toml（stripe CLI が保存したもの）から読む。
"""
import json
import subprocess
import sys
import time
from pathlib import Path

LIVE = "--live" in sys.argv
KEY_NAME = "live_mode_api_key" if LIVE else "test_mode_api_key"

cfg = (Path.home() / ".config/stripe/config.toml").read_text()
key = None
for line in cfg.splitlines():
    line = line.strip()
    if line.startswith(KEY_NAME):
        key = line.split("=", 1)[1].strip().strip("'\"")
        break
if not key:
    sys.exit(f"{KEY_NAME} not found in stripe config")

API = "https://api.stripe.com/v1"


def _curl(args):
    r = subprocess.run(
        ["curl", "-sS", "-u", f"{key}:"] + args,
        capture_output=True, text=True, check=True,
    )
    d = json.loads(r.stdout)
    if "error" in d:
        raise RuntimeError(json.dumps(d["error"], ensure_ascii=False)[:400])
    return d


def post(path, params):
    args = [f"{API}{path}"]
    for k, v in params.items():
        args += ["-d", f"{k}={v}"]
    return _curl(args)


def get(path, params=None):
    args = ["-G", f"{API}{path}"]
    for k, v in (params or {}).items():
        args += ["-d", f"{k}={v}"]
    return _curl(args)


# ─── カタログ定義（create_catalog.py と同一） ───
DOSES = [
    ("2.5mg", "2p5mg", "グレー"),
    ("5mg",   "5mg",   "パープル"),
    ("7.5mg", "7p5mg", "グリーン"),
    ("10mg",  "10mg",  "ピンク"),
    ("12.5mg","12p5mg","ブルー"),
    ("15mg",  "15mg",  "オレンジ"),
]
SETS = [
    (2,  0,  "2本セット"),
    (4,  1,  "4本セット（1ヶ月分）"),
    (8,  2,  "8本セット（2ヶ月分）"),
    (12, 3,  "12本セット（3ヶ月分）"),
    (24, 6,  "24本セット（6ヶ月分）"),
    (48, 12, "48本セット（12ヶ月分）"),
]
REGULAR = {
    "2.5mg": [13100, 15780, 29830, 41980, 77980, 149800],
    "5mg":   [19800, 28980, 53780, 74980, 139800, 265620],
    "7.5mg": [25500, 40780, 76300, 105980, 197980, 376162],
    "10mg":  [29800, 51300, 95980, 132980, 248980, 473062],
    "12.5mg":[31980, 60980, 113980, 157980, 294980, 572261],
    "15mg":  [53980, 68980, 128980, 179980, 334980, 656561],
}
OPTIONS = [
    ("ナウゼリン/ドンペリドン10mg（吐き気止め）10回分", "opt_nausea", 1000),
    ("防風通聖散（便秘改善）10包", "opt_bofu", 1000),
]

# 必要な lookup_key -> (商品名, 価格, price作成用パラメータ)
WANTED = {}
for dose, token, color in DOSES:
    for (pens, months, label), amount in zip(SETS, REGULAR[dose]):
        WANTED[f"mnj_{token}_{pens}pen"] = {
            "product_name": f"マンジャロ {dose}",
            "amount": amount,
            "nickname": label,
            "product_meta": {
                "metadata[drug]": "mounjaro",
                "metadata[dosage]": dose,
                "metadata[pen_color]": color,
                "metadata[catalog]": "kabukuri",
            },
            "price_meta": {
                "metadata[pens]": pens,
                "metadata[months]": months,
                "metadata[plan]": "regular",
            },
        }
for name, token, amount in OPTIONS:
    WANTED[token] = {
        "product_name": name,
        "amount": amount,
        "nickname": "",
        "product_meta": {"metadata[catalog]": "kabukuri", "metadata[category]": "option"},
        "price_meta": {"metadata[plan]": "option"},
    }

# ─── 1. 価格の存在確認・なければ商品ごと作成 ───
print(f"mode: {'LIVE' if LIVE else 'TEST'}")
prices = {}
starting_after = None
while True:
    params = {"limit": 100}
    if starting_after:
        params["starting_after"] = starting_after
    page = get("/prices", params)
    for p in page["data"]:
        if p.get("lookup_key"):
            prices[p["lookup_key"]] = p
    if not page.get("has_more"):
        break
    starting_after = page["data"][-1]["id"]

products_by_name = {}
missing = [k for k in WANTED if k not in prices]
if missing:
    print(f"missing prices: {len(missing)} -> creating")
    existing_products = get("/products", {"limit": 100, "active": "true"})
    products_by_name = {p["name"]: p for p in existing_products["data"]}
    for lk in missing:
        w = WANTED[lk]
        prod = products_by_name.get(w["product_name"])
        if not prod:
            prod = post("/products", {"name": w["product_name"], **w["product_meta"]})
            products_by_name[w["product_name"]] = prod
            time.sleep(0.1)
        price_params = {
            "product": prod["id"],
            "currency": "jpy",
            "unit_amount": w["amount"],
            "tax_behavior": "inclusive",
            "lookup_key": lk,
            **w["price_meta"],
        }
        if w["nickname"]:
            price_params["nickname"] = w["nickname"]
        prices[lk] = post("/prices", price_params)
        print(f"  created price: {lk} ({w['amount']}円)")
        time.sleep(0.1)
else:
    print("all prices exist")

# ─── 2. Payment Links（既存はmetadataのlookup_keyで再利用） ───
links = {}
starting_after = None
while True:
    params = {"limit": 100, "active": "true"}
    if starting_after:
        params["starting_after"] = starting_after
    page = get("/payment_links", params)
    for pl in page["data"]:
        lk = pl.get("metadata", {}).get("lookup_key")
        if lk:
            links[lk] = pl["url"]
    if not page.get("has_more"):
        break
    starting_after = page["data"][-1]["id"]

created = 0
for lk, w in WANTED.items():
    if lk in links:
        continue
    pl = post("/payment_links", {
        "line_items[0][price]": prices[lk]["id"],
        "line_items[0][quantity]": 1,
        "metadata[lookup_key]": lk,
        "metadata[site]": "kabukuri-clinic",
        # 決済手段はStripeダッシュボードの有効設定に自動追従（PayPay有効化後に自動で表示される）
    })
    links[lk] = pl["url"]
    created += 1
    print(f"  created link: {lk}")
    time.sleep(0.1)

print(f"payment links: reused={len(WANTED) - created}, created={created}")

# ─── 3. assets/payment-links.js を生成 ───
out = Path(__file__).resolve().parents[1] / "assets" / "payment-links.js"
mapping = {lk: links[lk] for lk in WANTED if lk in links}
js = (
    "/* Stripe Payment Links のマッピング（lookup_key -> URL）\n"
    "   このファイルは scripts/create_payment_links.py が自動生成する。手で編集しないこと。 */\n"
    f"const KBK_PAYMENT_LINKS = {json.dumps(mapping, ensure_ascii=False, indent=2)};\n"
)
out.write_text(js)
print(f"wrote {out} ({len(mapping)}/{len(WANTED)} links)")
