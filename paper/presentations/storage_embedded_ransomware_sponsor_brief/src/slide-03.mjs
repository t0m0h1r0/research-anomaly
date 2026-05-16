import { C, footer, panel, pill, row, slideBase, subtitle, title } from "./theme.mjs";

export async function slide03(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "INPUT CONTRACT | 10秒統計からML入力へ", 3, C.green);
  title(ctx, slide, "rawを持たず、10秒で切り出す");
  subtitle(ctx, slide, "ブロックストレージ装置では、特徴の取り方そのものがコストです。残すのはraw eventではなく、安い集計から作る固定shapeの統計列です。");

  panel(ctx, slide, { x: 82, y: 246, w: 496, h: 304, fill: C.white, stroke: C.line, title: "frame_10s: 装置が安く集計できる候補", accent: C.green });
  const rows = [
    ["count / bytes", "I/O量の強さ"],
    ["write ratio", "書き込み偏り"],
    ["mean LBA", "アクセス位置"],
    ["mean length", "転送長"],
    ["delta mean", "前窓からの変化"],
    ["optional telemetry", "安い圧縮/entropy風カウンタがある時だけ"],
    ["padding / mask", "未提供欄はloss/scoreから外す"],
  ];
  rows.forEach((texts, idx) => {
    const y = 304 + idx * 30;
    row(ctx, slide, {
      x: 112,
      y,
      w: 420,
      h: 24,
      fill: idx % 2 === 0 ? "#f8fafc" : "#eef2f7",
      stroke: "#d6dee9",
      columns: [160, 260],
      texts,
      colors: [C.ink, C.muted],
      bold: [true, false],
    });
  });

  panel(ctx, slide, {
    x: 642,
    y: 260,
    w: 274,
    h: 156,
    fill: C.white,
    stroke: C.line,
    body: "X: [batch=1, N, D]\ninitial: N=12, D=12\ncontext: 12 x 10s ~= 2 min\nscore: outside MNN graph\nthreshold: outside MNN graph",
  });
  panel(ctx, slide, {
    x: 964,
    y: 260,
    w: 236,
    h: 156,
    fill: C.purpleSoft,
    stroke: C.purple,
    title: "なぜ固定shapeか",
    body: "MNN変換、メモリ、CPU枠を同じ条件で比べるため。",
    accent: C.purple,
  });

  pill(ctx, slide, { text: "使わない: ファイルパス / プロセス名 / ランサムウェア署名 / ファイル本文scan", x: 178, y: 590, w: 520, h: 30, fill: C.redSoft, stroke: C.red, color: C.red });
  pill(ctx, slide, { text: "使う: SCSI/NVMe風メタデータ と 安い装置カウンタ", x: 762, y: 590, w: 410, h: 30, fill: C.blueSoft, stroke: C.blue, color: C.blue });
  footer(ctx, slide, "paper/sections/05_input_contract.tex, docs/04_embedded_constraints.md, docs/06_memory_aware_ae_candidates.md");
  return slide;
}
