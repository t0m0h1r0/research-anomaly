import { C, arrow, callout, claimLine, footer, panel, pill, slideBase, title } from "./theme.mjs";

export async function slide06(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "EVALUATION | 技術判断に必要な証拠", 6, C.blue);
  title(ctx, slide, "採用・縮小・棄却は、四つの証拠を見て決める", 92, 30);
  claimLine(ctx, slide, "精度だけで採用せず、offline比較、MNN parity、detector-data、10秒cadenceを同じゲートで判定する。", C.blue);
  callout(ctx, slide, { text: "すぐ導入できる、とは言わない", x: 850, y: 224, w: 292, h: 44, fill: C.ink, stroke: C.red, color: C.white });

  const gates = [
    ["1. offline検証", "benign-only学習、単純規則、AE-01..05、低誤警報で比較", C.blue, C.blueSoft],
    ["2. score parity", "同一入力でoffline scoreとMNN scoreの差を測る", C.purple, C.purpleSoft],
    ["3. detector-data", "重み、入力列、正規化、threshold、履歴が500 KB内か測る", C.amber, C.amberSoft],
    ["4. scheduling", "V volumeとQ inference slotで10秒cadenceを守れるか測る", C.green, C.greenSoft],
  ];
  gates.forEach(([head, body, accent, fill], idx) => {
    const x = 104 + idx * 286;
    panel(ctx, slide, { x, y: 272, w: 236, h: 134, fill, stroke: accent, title: head, body, accent });
    if (idx < gates.length - 1) arrow(ctx, slide, x + 248, 338, 28, "#64748b");
  });

  panel(ctx, slide, {
    x: 128,
    y: 472,
    w: 430,
    h: 92,
    fill: C.white,
    stroke: C.line,
    title: "主要な評価値",
    body: "誤警報の少なさ / 警告までの時間 / 警告前の被害量 / どの特徴がズレたか",
    accent: C.blue,
  });
  panel(ctx, slide, {
    x: 720,
    y: 472,
    w: 430,
    h: 92,
    fill: C.white,
    stroke: C.line,
    title: "制約に当たった時の縮小順",
    body: "feature数Dを減らす -> 系列長Nを短くする -> hidden sizeを縮める -> AE-05から単純候補へ戻す",
    accent: C.amber,
  });

  pill(ctx, slide, { text: "固定済み: block I/O観測境界、10秒統計、AE候補、device-fit gates", x: 184, y: 604, w: 540, h: 30, fill: C.greenSoft, stroke: C.green, color: C.green });
  pill(ctx, slide, { text: "未主張: 検出性能、MNN readiness、500KB内に収まった結論、実運用早期警告", x: 792, y: 604, w: 410, h: 30, fill: C.redSoft, stroke: C.red, color: C.red });
  footer(ctx, slide, "paper/sections/07_evaluation_plan.tex, paper/sections/08_mnn_implementation_plan.tex, docs/evidence/manuscript_claim_gate_matrix.md");
  return slide;
}
