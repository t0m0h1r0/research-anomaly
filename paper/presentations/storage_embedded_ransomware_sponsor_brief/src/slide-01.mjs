import { C, arrow, callout, circuitTrace, claimLine, footer, panel, pill, slideBase, title } from "./theme.mjs";

export async function slide01(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "TECHNICAL SCOPE | ブロックストレージ組み込み", 1, C.blue);
  title(ctx, slide, "ブロックI/Oだけで、異常検知の入力を作れるかを測る", 92, 30);
  claimLine(ctx, slide, "ファイルパスやプロセス名を使わず、要求時刻・read/write・LBA・lengthから10秒統計を作る。", C.blue);
  circuitTrace(ctx, slide, { x: 710, y: 246, w: 420, h: 218, color: C.blue, opacityFill: C.blueSoft });
  callout(ctx, slide, { text: "観測は装置境界で取れる軽量メタデータだけ", x: 752, y: 498, w: 334, h: 48, fill: C.ink, stroke: C.blue, color: C.white });

  panel(ctx, slide, {
    x: 76,
    y: 288,
    w: 190,
    h: 96,
    fill: "#f8fafc",
    title: "Host / VM",
    body: "アプリ/OS詳細に依存しない",
  });
  arrow(ctx, slide, 292, 336, 70, "#64748b");
  panel(ctx, slide, {
    x: 384,
    y: 272,
    w: 250,
    h: 128,
    fill: C.blueSoft,
    stroke: C.blue,
    title: "Block storage controller",
    body: "timestamp / read-write / LBA / length\nを受ける境界",
    accent: C.blue,
  });
  arrow(ctx, slide, 664, 336, 70, "#64748b");
  panel(ctx, slide, {
    x: 760,
    y: 288,
    w: 190,
    h: 96,
    fill: "#f8fafc",
    title: "Protected volumes",
    body: "多数ボリュームを10秒間隔で見る",
  });

  panel(ctx, slide, {
    x: 134,
    y: 450,
    w: 404,
    h: 116,
    fill: "#f7fffb",
    stroke: "#22c55e",
    title: "組み込み検知パス",
    body: "",
    accent: "#22c55e",
  });
  pill(ctx, slide, { text: "collector\n軽量カウンタ集計", x: 168, y: 506, w: 96, h: 42, fill: C.white, stroke: C.green, color: C.green });
  pill(ctx, slide, { text: "feature ring\n統計列を保持", x: 288, y: 506, w: 100, h: 42, fill: C.white, stroke: C.green, color: C.green });
  pill(ctx, slide, { text: "AE score\n再構成誤差を計算", x: 412, y: 506, w: 100, h: 42, fill: C.white, stroke: C.green, color: C.green });

  panel(ctx, slide, {
    x: 96,
    y: 570,
    w: 280,
    h: 76,
    fill: C.white,
    stroke: C.blue,
    title: "観測境界",
    body: "",
    accent: C.blue,
  });
  panel(ctx, slide, {
    x: 500,
    y: 570,
    w: 280,
    h: 76,
    fill: C.white,
    stroke: C.green,
    title: "検証対象",
    body: "",
    accent: C.green,
  });
  panel(ctx, slide, {
    x: 888,
    y: 570,
    w: 280,
    h: 76,
    fill: C.white,
    stroke: C.red,
    title: "未主張",
    body: "",
    accent: C.red,
  });
  ctx.addText(slide, { text: "ブロック要求メタデータだけ", x: 122, y: 616, w: 230, h: 18, fontSize: 10, color: C.ink, face: "Hiragino Sans" });
  ctx.addText(slide, { text: "軽量MLの成立性を測る", x: 526, y: 616, w: 230, h: 18, fontSize: 10, color: C.ink, face: "Hiragino Sans" });
  ctx.addText(slide, { text: "性能・早期警告は未主張", x: 914, y: 616, w: 230, h: 18, fontSize: 10, color: C.ink, face: "Hiragino Sans" });
  footer(ctx, slide, "docs/interface/ResearchBrief.md, docs/04_embedded_constraints.md, paper/sections/05_input_contract.tex");
  return slide;
}
