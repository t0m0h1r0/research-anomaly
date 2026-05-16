import { C, arrow, callout, claimLine, footer, panel, pill, slideBase, title } from "./theme.mjs";

export async function slide01(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "TECHNICAL SCOPE | ブロックストレージ組み込み", 1, C.blue);
  title(ctx, slide, "装置境界で取れる情報だけを、10秒統計に変換する", 92, 30);
  claimLine(ctx, slide, "アプリ/OS側の情報は入力に入れず、block request metadata -> frame_10s -> AE score の一本の経路を検証する。", C.blue);

  panel(ctx, slide, {
    x: 86,
    y: 258,
    w: 192,
    h: 126,
    fill: "#f8fafc",
    stroke: C.line,
    title: "Host / VM",
    body: "アプリ名、プロセス名、ファイルパスは入力にしない",
  });
  arrow(ctx, slide, 302, 320, 54, C.muted);

  panel(ctx, slide, {
    x: 374,
    y: 244,
    w: 230,
    h: 154,
    fill: C.blueSoft,
    stroke: C.blue,
    title: "観測境界",
    body: "timestamp\nread/write\nLBA\nlength",
    accent: C.blue,
  });
  callout(ctx, slide, { text: "ここだけを見る", x: 410, y: 410, w: 156, h: 38, fill: C.ink, stroke: C.blue, color: C.white });
  arrow(ctx, slide, 628, 320, 54, C.muted);

  panel(ctx, slide, {
    x: 700,
    y: 244,
    w: 230,
    h: 154,
    fill: C.greenSoft,
    stroke: C.green,
    title: "10秒統計",
    body: "count / bytes\nwrite ratio\nmean LBA / length\noptional counters",
    accent: C.green,
  });
  arrow(ctx, slide, 954, 320, 54, C.muted);

  panel(ctx, slide, {
    x: 1026,
    y: 258,
    w: 168,
    h: 126,
    fill: C.purpleSoft,
    stroke: C.purple,
    title: "AE score",
    body: "再構成誤差を計算\n判定は外側で行う",
    accent: C.purple,
  });

  panel(ctx, slide, {
    x: 96,
    y: 492,
    w: 318,
    h: 112,
    fill: C.white,
    stroke: C.blue,
    title: "使う情報",
    body: "ブロック要求メタデータと、装置側で低コストに持てるカウンタ",
    accent: C.blue,
  });
  panel(ctx, slide, {
    x: 482,
    y: 492,
    w: 318,
    h: 112,
    fill: C.white,
    stroke: C.green,
    title: "検証する経路",
    body: "collector -> feature ring -> AE score の流れが、10秒間隔で成立するか",
    accent: C.green,
  });
  panel(ctx, slide, {
    x: 868,
    y: 492,
    w: 318,
    h: 112,
    fill: C.white,
    stroke: C.red,
    title: "使わない情報",
    body: "ファイル本文、ファイル名、プロセス名、ランサムウェア署名",
    accent: C.red,
  });
  pill(ctx, slide, { text: "未主張: 検出性能・早期警告・導入可否", x: 396, y: 622, w: 488, h: 28, fill: C.redSoft, stroke: C.red, color: C.red });
  footer(ctx, slide, "docs/interface/ResearchBrief.md, docs/04_embedded_constraints.md, paper/sections/05_input_contract.tex");
  return slide;
}
