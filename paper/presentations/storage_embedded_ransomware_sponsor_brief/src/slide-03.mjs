import { C, claimLine, footer, panel, pill, row, slideBase, title } from "./theme.mjs";

export async function slide03(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "INPUT CONTRACT | 10秒統計からML入力へ", 3, C.green);
  title(ctx, slide, "生イベントを保存せず、10秒統計を入力にする");
  claimLine(ctx, slide, "MLに渡すのは生イベント列ではなく、装置内で低コストに集計できる固定長の10秒統計列である。", C.green);

  panel(ctx, slide, { x: 82, y: 246, w: 496, h: 304, fill: C.white, stroke: C.line, title: "frame_10s: 装置で低コストに集計できる候補", accent: C.green });
  const rows = [
    ["count / bytes", "I/O量の強さ"],
    ["write ratio", "書き込み偏り"],
    ["mean LBA", "アクセス位置"],
    ["mean length", "転送長"],
    ["delta mean", "前窓からの変化"],
    ["optional telemetry", "低コストな圧縮/entropy系カウンタがある場合のみ"],
    ["padding / mask", "未提供の列はloss/scoreから外す"],
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
    title: "固定長にする理由",
    body: "MNN変換、メモリ、CPU枠を同じ条件で比べるため。",
    accent: C.purple,
  });

  pill(ctx, slide, { text: "使わない: ファイルパス / プロセス名 / ランサムウェア署名 / ファイル本文スキャン", x: 178, y: 590, w: 520, h: 30, fill: C.redSoft, stroke: C.red, color: C.red });
  pill(ctx, slide, { text: "使う: SCSI/NVMe相当のメタデータ と 軽量カウンタ", x: 762, y: 590, w: 410, h: 30, fill: C.blueSoft, stroke: C.blue, color: C.blue });
  footer(ctx, slide, "paper/sections/05_input_contract.tex, docs/04_embedded_constraints.md, docs/06_memory_aware_ae_candidates.md");
  return slide;
}
