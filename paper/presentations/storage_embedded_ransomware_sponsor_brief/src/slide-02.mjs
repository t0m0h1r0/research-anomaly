import { C, arrow, callout, claimLine, footer, panel, slideBase, title } from "./theme.mjs";

export async function slide02(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "DECISION FRAME | このプレゼンで決めること", 2, C.green);
  title(ctx, slide, "導入判断の前に、候補を落とす条件を決める", 92, 30);
  claimLine(ctx, slide, "いま必要なのは採用可否の結論ではなく、次の実験で候補を採用・縮小・棄却する判定条件である。", C.green);
  callout(ctx, slide, { text: "残す候補より先に、止める条件を固定する", x: 776, y: 224, w: 382, h: 44, fill: C.ink, stroke: C.green, color: C.white });

  const cards = [
    ["1. 単純規則で足りるか", "write ratio、I/O強度、LBA移動だけで説明できるならAEは縮小または棄却する", C.blue, C.blueSoft],
    ["2. AEのどこまで必要か", "Dense、時系列文脈、局所時間特徴、CNN-GRUを同じ入力で順番に比較する", C.purple, C.purpleSoft],
    ["3. 装置に載るか", "500 KB detector-data、MNN score parity、10秒cadenceのCPU/slotを分けて測る", C.amber, C.amberSoft],
    ["4. 次の証拠は何か", "manifest付き実験、MNN変換、memory harnessのどれが意思決定を進めるかを明確にする", C.green, C.greenSoft],
  ];
  cards.forEach(([head, body, accent, fill], idx) => {
    const x = 86 + idx * 292;
    panel(ctx, slide, { x, y: 278, w: 238, h: 178, fill, stroke: accent, title: head, body, accent });
    if (idx < cards.length - 1) arrow(ctx, slide, x + 250, 364, 32, "#64748b");
  });

  panel(ctx, slide, {
    x: 126,
    y: 518,
    w: 450,
    h: 88,
    fill: C.white,
    stroke: C.green,
    title: "進める条件",
    body: "単純規則を超える説明価値があり、MNN変換後もscoreが一致し、per-volume状態とschedulingが予算内に収まる見込みを測れる。",
    accent: C.green,
  });
  panel(ctx, slide, {
    x: 704,
    y: 518,
    w: 450,
    h: 88,
    fill: C.white,
    stroke: C.red,
    title: "止める条件",
    body: "単純規則で十分、cheap featureが不足、MNN parityが崩れる、500 KBまたは10秒cadenceのどちらかを満たせない。",
    accent: C.red,
  });

  footer(ctx, slide, "docs/03_PROJECT_RULES.md, docs/evidence/manuscript_claim_gate_matrix.md, docs/04_embedded_constraints.md");
  return slide;
}
