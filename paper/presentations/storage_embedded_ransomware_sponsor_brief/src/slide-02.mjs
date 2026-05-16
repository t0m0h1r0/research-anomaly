import { C, arrow, callout, claimLine, footer, panel, slideBase, title } from "./theme.mjs";

export async function slide02(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "DECISION FRAME | 判定基準", 2, C.green);
  title(ctx, slide, "導入可否の前に、次実験の判定基準を決める", 92, 30);
  claimLine(ctx, slide, "決める対象は採用可否ではなく、単純規則・AE複雑度・装置制約で候補を進めるか止めるかの基準である。", C.green);
  callout(ctx, slide, { text: "残す候補より先に、止める条件を固定する", x: 776, y: 224, w: 382, h: 44, fill: C.ink, stroke: C.green, color: C.white });

  const cards = [
    ["1. 単純規則で足りるか", "write ratio、I/O強度、LBA移動で説明できるならAE候補を縮小または棄却する", C.blue, C.blueSoft],
    ["2. どの演算まで必要か", "Dense、時系列文脈、局所時間特徴、CNN-GRUを同じ入力で順番に比べる", C.purple, C.purpleSoft],
    ["3. 装置制約に収まるか", "500 KB detector-data、MNN score一致、10秒間隔のCPU枠を別々に測る", C.amber, C.amberSoft],
    ["4. 次に何を測るか", "manifest付き実験、MNN変換、メモリ測定のどれが判断を進めるかを決める", C.green, C.greenSoft],
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
    body: "単純規則を超える説明価値があり、MNN変換後のscore差、per-volume状態量、10秒間隔の見込みを測れる。",
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
    body: "単純規則で十分、安価な特徴量が不足、MNN score一致が崩れる、500 KBまたは10秒間隔のどちらかを満たせない。",
    accent: C.red,
  });

  footer(ctx, slide, "docs/03_PROJECT_RULES.md, docs/evidence/manuscript_claim_gate_matrix.md, docs/04_embedded_constraints.md");
  return slide;
}
