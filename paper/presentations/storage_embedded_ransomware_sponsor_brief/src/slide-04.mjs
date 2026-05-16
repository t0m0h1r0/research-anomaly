import { C, footer, pill, row, slideBase, subtitle, title } from "./theme.mjs";

export async function slide04(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "MODEL CANDIDATES | AE-01..05 の技術的な意味", 4, C.purple);
  title(ctx, slide, "AE-01..05は、複雑さを裁く階段");
  subtitle(ctx, slide, "初期値はN=12, D=12。parameter/raw weightは計画見積もりで、MNN変換後サイズや一時scratchは別に測ります。");

  const x = 76;
  const y0 = 234;
  const cols = [92, 258, 318, 172, 288];
  row(ctx, slide, {
    x,
    y: y0,
    w: 1128,
    h: 34,
    fill: C.ink,
    stroke: C.ink,
    columns: cols,
    texts: ["ID", "candidate", "operator role", "planning size", "評価する目的"],
    colors: [C.white, C.white, C.white, C.white, C.white],
    bold: [true, true, true, true, true],
  });
  const rows = [
    ["AE-01", "Flat MLP", "flattenした2分窓を圧縮", "9,944-20,768 params", "粗い統計だけでズレが見えるか"],
    ["AE-02", "Two-level Dense", "10秒ごとの圧縮 + 系列圧縮", "5,836 params", "時間演算なしで足りるか"],
    ["AE-03", "GRU context", "順序と過去文脈を付与", "7,052 params", "履歴を見ないと説明できないか"],
    ["AE-04", "Temporal Conv1D", "近傍時間の局所変化を抽出", "5,684 params", "GRUなしの時間特徴で足りるか"],
    ["AE-05", "Tiny CNN-GRU", "特徴混合 + 文脈 + bottleneck", "8,052 params", "複合モデルの追加演算に価値があるか"],
  ];
  const fills = [C.purpleSoft, C.blueSoft, C.greenSoft, C.cyanSoft, C.amberSoft];
  const strokes = [C.purple, C.blue, C.green, C.cyan, "#f97316"];
  rows.forEach((texts, idx) => {
    row(ctx, slide, {
      x,
      y: y0 + 44 + idx * 58,
      w: 1128,
      h: 54,
      fill: fills[idx],
      stroke: strokes[idx],
      columns: cols,
      texts,
      colors: [strokes[idx], C.blue, C.ink, C.muted, C.ink],
      bold: [true, true, false, false, false],
    });
  });

  pill(ctx, slide, { text: "選定方針: 簡単な候補で説明できるなら、そこで止める", x: 180, y: 604, w: 420, h: 30, fill: C.greenSoft, stroke: C.green, color: C.green });
  pill(ctx, slide, { text: "未主張: 実測前に性能順位・MNN適合・500KB内に収まった結論を言わない", x: 682, y: 604, w: 440, h: 30, fill: C.redSoft, stroke: C.red, color: C.red });
  footer(ctx, slide, "docs/06_memory_aware_ae_candidates.md, paper/sections/06_autoencoder_candidates.tex");
  return slide;
}
