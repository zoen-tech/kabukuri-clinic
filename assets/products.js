/* カブクリ 商品マスタ（税込価格）
   出典: repo_kabukuri/finance/stripe/create_catalog.py（=medical/pricing/pricing-table.md 2026-05-14）
   価格を変更する場合は Stripe カタログ・payment-links.json と必ず同時に更新すること */

const KBK_DOSES = [
  { dose: "2.5mg",  token: "2p5mg"  },
  { dose: "5mg",    token: "5mg"    },
  { dose: "7.5mg",  token: "7p5mg"  },
  { dose: "10mg",   token: "10mg"   },
  { dose: "12.5mg", token: "12p5mg" },
  { dose: "15mg",   token: "15mg"   },
];

const KBK_SETS = [
  { pens: 2,  label: "2本セット",              note: ""        },
  { pens: 4,  label: "4本セット（1ヶ月分）",   note: "1ヶ月分"  },
  { pens: 8,  label: "8本セット（2ヶ月分）",   note: "2ヶ月分"  },
  { pens: 12, label: "12本セット（3ヶ月分）",  note: "3ヶ月分"  },
  { pens: 24, label: "24本セット（6ヶ月分）",  note: "6ヶ月分"  },
  { pens: 48, label: "48本セット（12ヶ月分）", note: "12ヶ月分" },
];

/* dose -> [2,4,8,12,24,48本] の税込価格 */
const KBK_PRICES = {
  "2.5mg":  [13100, 15780, 29830, 41980, 77980, 149800],
  "5mg":    [19800, 28980, 53780, 74980, 139800, 265620],
  "7.5mg":  [25500, 40780, 76300, 105980, 197980, 376162],
  "10mg":   [29800, 51300, 95980, 132980, 248980, 473062],
  "12.5mg": [31980, 60980, 113980, 157980, 294980, 572261],
  "15mg":   [53980, 68980, 128980, 179980, 334980, 656561],
};

const KBK_OPTIONS = [
  { name: "ナウゼリン/ドンペリドン10mg（吐き気止め）10回分", token: "opt_nausea", price: 1000 },
  { name: "防風通聖散（便秘改善）10包",                       token: "opt_bofu",   price: 1000 },
];

function kbkLookupKey(doseToken, pens) {
  return `mnj_${doseToken}_${pens}pen`;
}

function kbkYen(n) {
  return "¥" + n.toLocaleString("ja-JP");
}
