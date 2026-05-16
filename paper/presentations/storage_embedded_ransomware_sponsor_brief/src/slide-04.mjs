import { C, arrow, claimLine, footer, panel, pill, slideBase, title } from "./theme.mjs";

export async function slide04(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "MODEL CANDIDATES | AE-01..05 の技術的な意味", 4, C.purple);
  title(ctx, slide, "AE-01..05で、どの追加演算が効くかを切り分ける");
  claimLine(ctx, slide, "各候補は性能順位を決めるためではなく、圧縮・文脈・局所時間特徴・特徴混合の必要性を一つずつ確かめるために並べる。", C.purple);

  const candidates = [
    ["AE-01", "Flat MLP", "粗い統計だけで差分が見えるか", C.blue, C.blueSoft],
    ["AE-02", "Two-level Dense", "10秒単位の圧縮で十分か", C.green, C.greenSoft],
    ["AE-03", "GRU context", "順序と過去文脈が必要か", C.purple, C.purpleSoft],
    ["AE-04", "Temporal Conv1D", "局所的な時間変化が必要か", C.cyan, C.cyanSoft],
    ["AE-05", "Tiny CNN-GRU", "特徴混合と文脈の組合せが必要か", C.amber, C.amberSoft],
  ];
  candidates.forEach(([id, name, body, accent, fill], idx) => {
    const x = 86 + idx * 226;
    panel(ctx, slide, {
      x,
      y: 258,
      w: 184,
      h: 162,
      fill,
      stroke: accent,
      title: id,
      body: `${name}\n\n${body}`,
      accent,
    });
    if (idx < candidates.length - 1) arrow(ctx, slide, x + 194, 338, 26, C.muted);
  });

  panel(ctx, slide, {
    x: 96,
    y: 472,
    w: 318,
    h: 104,
    fill: C.white,
    stroke: C.green,
    title: "わかること 1",
    body: "AE-01/02で十分なら、時系列演算や複合モデルへ進めない。",
    accent: C.green,
  });
  panel(ctx, slide, {
    x: 482,
    y: 472,
    w: 318,
    h: 104,
    fill: C.white,
    stroke: C.purple,
    title: "わかること 2",
    body: "AE-03/04で差が出るなら、過去文脈か局所時間特徴が必要になる。",
    accent: C.purple,
  });
  panel(ctx, slide, {
    x: 868,
    y: 472,
    w: 318,
    h: 104,
    fill: C.white,
    stroke: C.amber,
    title: "わかること 3",
    body: "AE-05だけが残るなら、複合演算の価値をMNNとメモリで再確認する。",
    accent: C.amber,
  });

  pill(ctx, slide, { text: "未主張: 実測前に性能順位・MNN適合・500 KB内に収まった結論を言わない", x: 336, y: 614, w: 608, h: 30, fill: C.redSoft, stroke: C.red, color: C.red });
  footer(ctx, slide, "docs/06_memory_aware_ae_candidates.md, paper/sections/06_autoencoder_candidates.tex");
  return slide;
}
