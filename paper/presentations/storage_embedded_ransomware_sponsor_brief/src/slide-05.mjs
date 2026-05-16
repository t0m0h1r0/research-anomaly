import { C, arrow, claimLine, footer, panel, slideBase, title } from "./theme.mjs";

export async function slide05(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "RESOURCE BUDGET | MLに使える資源は小さい", 5, C.amber);
  title(ctx, slide, "重みは候補で変わり、状態はボリューム数で増える", 92, 29);
  claimLine(ctx, slide, "500 KBの見積もりは、候補ごとに変わる重みと、ボリュームごとに増える状態を分けて測らないと判断できない。", C.amber);

  panel(ctx, slide, {
    x: 86,
    y: 252,
    w: 286,
    h: 150,
    fill: C.white,
    stroke: C.blue,
    title: "モデル重み",
    body: "AE候補ごとに変わる\nMNN変換後サイズを測る\n共有できるかも実装で確認",
    accent: C.blue,
  });
  arrow(ctx, slide, 392, 322, 54, C.muted);

  panel(ctx, slide, {
    x: 466,
    y: 252,
    w: 286,
    h: 150,
    fill: C.white,
    stroke: C.green,
    title: "ボリューム状態",
    body: "入力列、正規化値、しきい値、score履歴\nボリューム数Vに比例して増える",
    accent: C.green,
  });
  arrow(ctx, slide, 772, 322, 54, C.muted);

  panel(ctx, slide, {
    x: 846,
    y: 252,
    w: 286,
    h: 150,
    fill: C.amberSoft,
    stroke: C.amber,
    title: "detector-data",
    body: "重み + 状態を分けて集計\n500 KBは測定で置き換える上限目安",
    accent: C.amber,
  });

  panel(ctx, slide, {
    x: 86,
    y: 442,
    w: 470,
    h: 132,
    fill: C.white,
    stroke: C.line,
    title: "単一ボリュームで見る式",
    accent: C.amber,
    body: "detector_data ~= model_weights + state_per_volume\n\nstate_per_volume = input sequence + normalization + threshold + score history",
  });
  panel(ctx, slide, {
    x: 626,
    y: 442,
    w: 506,
    h: 132,
    fill: C.white,
    stroke: C.line,
    title: "装置全体で見る式",
    accent: C.green,
    body: "M_persistent(V) = M_shared_runtime + M_shared_weights + V x state_per_volume\n\nM_peak(V,Q) = M_persistent(V) + Q x transient_scratch",
  });

  panel(ctx, slide, {
    x: 86,
    y: 596,
    w: 326,
    h: 50,
    fill: C.blueSoft,
    stroke: C.blue,
    title: "重み: AE-01..05で変わる",
    body: "",
    accent: C.blue,
  });
  panel(ctx, slide, {
    x: 476,
    y: 596,
    w: 326,
    h: 50,
    fill: C.greenSoft,
    stroke: C.green,
    title: "状態: N/D/履歴で変わる",
    body: "",
    accent: C.green,
  });
  panel(ctx, slide, {
    x: 866,
    y: 596,
    w: 326,
    h: 50,
    fill: C.purpleSoft,
    stroke: C.purple,
    title: "scratch: Q推論slotで変わる",
    body: "",
    accent: C.purple,
  });

  footer(ctx, slide, "docs/04_embedded_constraints.md, docs/memo/500kb_budget_reconciliation.md, paper/sections/08_mnn_implementation_plan.tex");
  return slide;
}
