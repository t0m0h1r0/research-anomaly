import { C, arrow, footer, panel, pill, slideBase, subtitle, title } from "./theme.mjs";

export async function slide01(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "TECHNICAL SCOPE | ブロックストレージ組み込み", 1, C.blue);
  title(ctx, slide, "研究対象は、ブロックI/Oの流れに埋め込む軽量な異常検知");
  subtitle(ctx, slide, "ホストのプロセス名やファイルパスに頼らず、装置側で安く取れる要求メタデータだけから、AE候補に渡す価値があるかを検証します。");

  panel(ctx, slide, {
    x: 76,
    y: 274,
    w: 190,
    h: 96,
    title: "Host / VM",
    body: "アプリやOSの詳細には依存しない",
  });
  arrow(ctx, slide, 292, 322, 70);
  panel(ctx, slide, {
    x: 384,
    y: 258,
    w: 250,
    h: 128,
    fill: C.blueSoft,
    stroke: C.blue,
    title: "Block storage controller",
    body: "timestamp / read-write / LBA / length\nなどを受ける境界",
    accent: C.blue,
  });
  arrow(ctx, slide, 664, 322, 70);
  panel(ctx, slide, {
    x: 760,
    y: 274,
    w: 190,
    h: 96,
    title: "Protected volumes",
    body: "多数volumeを10秒cadenceで見る",
  });

  panel(ctx, slide, {
    x: 438,
    y: 430,
    w: 404,
    h: 116,
    fill: "#f7fffb",
    stroke: "#22c55e",
    title: "組み込み検知パス",
    body: "",
    accent: "#22c55e",
  });
  pill(ctx, slide, { text: "collector\n安いcounter集計", x: 472, y: 486, w: 96, h: 42, fill: C.white, stroke: C.green, color: C.green });
  pill(ctx, slide, { text: "feature ring\nN x Dを保持", x: 592, y: 486, w: 100, h: 42, fill: C.white, stroke: C.green, color: C.green });
  pill(ctx, slide, { text: "AE score\n再構成誤差を外側で判定", x: 716, y: 486, w: 100, h: 42, fill: C.white, stroke: C.green, color: C.green });

  panel(ctx, slide, {
    x: 92,
    y: 552,
    w: 280,
    h: 80,
    title: "観測境界",
    body: "ブロック要求メタデータだけを前提にする",
    accent: C.blue,
  });
  panel(ctx, slide, {
    x: 500,
    y: 552,
    w: 280,
    h: 80,
    title: "検証対象",
    body: "装置内で回せるほど軽いMLかを測る",
    accent: C.green,
  });
  panel(ctx, slide, {
    x: 888,
    y: 552,
    w: 280,
    h: 80,
    title: "未主張",
    body: "検出性能や実運用の早期警告はまだ主張しない",
    accent: C.red,
  });
  footer(ctx, slide, "docs/interface/ResearchBrief.md, docs/04_embedded_constraints.md, paper/sections/05_input_contract.tex");
  return slide;
}
