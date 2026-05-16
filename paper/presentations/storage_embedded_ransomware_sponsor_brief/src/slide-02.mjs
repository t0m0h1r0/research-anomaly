import { C, arrow, footer, panel, slideBase, subtitle, title } from "./theme.mjs";

export async function slide02(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "DECISION FRAME | このプレゼンで決めること", 2, C.green);
  title(ctx, slide, "ゴールは導入判断ではなく、次に捨てる候補と測る証拠を決めること");
  subtitle(ctx, slide, "AEを前提にせず、単純規則・入力契約・装置制約の順に候補を削り、残った仮説だけを実装検証へ進めます。");

  const cards = [
    ["1. 単純規則で足りるか", "write ratio、I/O強度、LBA移動だけで説明できるならAEは縮小または棄却する", C.blue, C.blueSoft],
    ["2. AEのどこまで必要か", "Dense、時系列文脈、局所時間特徴、CNN-GRUを同じ入力で順番に比較する", C.purple, C.purpleSoft],
    ["3. 装置に載るか", "500 KB detector-data、MNN score parity、10秒cadenceのCPU/slotを分けて測る", C.amber, C.amberSoft],
    ["4. 次の証拠は何か", "manifest付き実験、MNN変換、memory harnessのどれが意思決定を進めるかを明確にする", C.green, C.greenSoft],
  ];
  cards.forEach(([head, body, accent, fill], idx) => {
    const x = 86 + idx * 292;
    panel(ctx, slide, { x, y: 268, w: 238, h: 178, fill, stroke: accent, title: head, body, accent });
    if (idx < cards.length - 1) arrow(ctx, slide, x + 250, 354, 32);
  });

  panel(ctx, slide, {
    x: 126,
    y: 506,
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
    y: 506,
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

