# Journal Tiers

Use this whitelist before considering any fallback source.
For the non-whitelist CSSCI floor, use the fixed local file `cnki-authority-retriever/references/cssci_2025_2026_source_journals.tsv`.

## A+

- 中国社会科学
- 经济研究
- 管理世界

## A

- 经济学(季刊)
- 中国工业经济
- 世界经济
- 金融研究
- 管理科学学报
- 新华文摘(全文转载)

## B

- 会计研究
- 财经研究
- 财贸经济
- 国际经济评论
- 经济科学
- 经济理论与经济管理
- 国际金融研究
- 南开经济研究
- 数量经济技术经济研究
- 统计研究
- 中国农村经济

## Ordering Rule

Sort by:

1. tier
2. retrieval channels hit
3. cited count
4. paragraph-level fit
5. year

Use `其他来源` only when all of the following hold:

1. the whitelist cannot support a specific China-facing claim
2. the fallback record is still a journal article
3. the fallback journal appears in the fixed local CSSCI list for `2025-2026`

Do not use non-CSSCI journals as fallback.
Do not use theses, books, conference proceedings, newspapers, or other non-journal records at any stage.
