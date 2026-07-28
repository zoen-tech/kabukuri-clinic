/* カブクリ 商品マスタ（税込価格）
   出典: repo_kabukuri/medical/pricing/pricing-table.md の改定価格（2026年8月1日〜掲載開始）
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
  "2.5mg":  [8980, 11980, 23480, 31980, 59880, 115200],
  "5mg":    [14980, 22480, 44580, 62880, 119760, 235200],
  "7.5mg":  [19980, 31980, 61980, 89880, 158380, 313800],
  "10mg":   [23980, 42280, 77980, 105980, 198800, 393800],
  "12.5mg": [25980, 49780, 91680, 124580, 245800, 489800],
  "15mg":   [30980, 55580, 102280, 151800, 293800, 585800],
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
