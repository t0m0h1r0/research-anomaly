import { C, claimLine, footer, panel, pill, row, slideBase, title } from "./theme.mjs";

export async function slide05(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "RESOURCE BUDGET | MLに使える資源は小さい", 5, C.amber);
  title(ctx, slide, "500 KBの対象は、重みだけでなくボリュームごとの状態である", 92, 28);
  claimLine(ctx, slide, "予算に入れるのはモデル重み、入力列、正規化値、しきい値、スコア履歴であり、共有runtimeや一時scratchとは分けて測る。", C.amber);

  panel(ctx, slide, {
    x: 86,
    y: 250,
    w: 466,
    h: 318,
    fill: C.white,
    stroke: C.line,
    title: "ボリュームごとの detector-data 目標",
    accent: C.amber,
  });
  const budgetRows = [
    ["model weights + quant metadata", "<= 360 KB"],
    ["10s input sequence buffers", "<= 64 KB"],
    ["normalization / threshold", "<= 24 KB"],
    ["score history / explanation", "<= 16 KB"],
    ["metadata + margin", "<= 36 KB"],
  ];
  budgetRows.forEach((texts, idx) => {
    row(ctx, slide, {
      x: 116,
      y: 316 + idx * 42,
      w: 386,
      h: 28,
      fill: "#eef2f7",
      stroke: [C.blue, C.green, C.purple, C.cyan, "#f97316"][idx],
      columns: [286, 100],
      texts,
      colors: [C.ink, [C.blue, C.green, C.purple, C.cyan, "#f97316"][idx]],
      bold: [false, true],
    });
  });
  ctx.addText(slide, {
    text: "上限目安。実装・MNN変換後の測定で置き換える。",
    x: 118,
    y: 530,
    w: 370,
    h: 20,
    fontSize: 8.5,
    color: C.muted,
    face: "Hiragino Sans",
  });

  panel(ctx, slide, {
    x: 632,
    y: 252,
    w: 500,
    h: 132,
    fill: C.white,
    stroke: C.line,
    title: "aggregate device-fit view",
    accent: C.green,
    body: "M_persistent(V) = M_shared_runtime + M_shared_weights + V x state_per_volume\n\nM_peak(V,Q) = M_persistent(V) + Q x transient_scratch",
  });

  pill(ctx, slide, { text: "V ~= 2000\n多数ボリュームを10秒間隔で採点", x: 632, y: 422, w: 170, h: 118, fill: C.blueSoft, stroke: C.blue, color: C.blue });
  pill(ctx, slide, { text: "Q slots\n同時推論slotに応じて一時scratchが増える", x: 822, y: 422, w: 170, h: 118, fill: C.purpleSoft, stroke: C.purple, color: C.purple });
  pill(ctx, slide, { text: "CPU window\n10秒内に全ボリュームを採点できるか", x: 1012, y: 422, w: 170, h: 118, fill: C.greenSoft, stroke: C.green, color: C.green });

  footer(ctx, slide, "docs/04_embedded_constraints.md, docs/memo/500kb_budget_reconciliation.md, paper/sections/08_mnn_implementation_plan.tex");
  return slide;
}
