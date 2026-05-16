export const C = {
  ink: "#111827",
  muted: "#64748b",
  faint: "#eef2f7",
  bg: "#f8fafc",
  line: "#cbd5e1",
  blue: "#2563eb",
  blueSoft: "#dbeafe",
  green: "#15803d",
  greenSoft: "#dcfce7",
  purple: "#7c3aed",
  purpleSoft: "#ede9fe",
  amber: "#b45309",
  amberSoft: "#fef3c7",
  cyan: "#0891b2",
  cyanSoft: "#cffafe",
  red: "#dc2626",
  redSoft: "#fee2e2",
  white: "#ffffff",
};

export const fonts = {
  title: "Hiragino Mincho ProN",
  body: "Hiragino Sans",
  mono: "Menlo",
};

export function slideBase(presentation, ctx, section, pageNo, accent = C.blue) {
  const slide = presentation.slides.add();
  ctx.addShape(slide, { x: 0, y: 0, w: ctx.W, h: ctx.H, fill: C.bg });
  ctx.addShape(slide, { x: 0, y: 0, w: ctx.W, h: 22, fill: C.ink });
  ctx.addShape(slide, { x: 58, y: 52, w: 8, h: 8, fill: accent });
  ctx.addText(slide, {
    text: section,
    x: 76,
    y: 44,
    w: 720,
    h: 24,
    fontSize: 12,
    color: "#475569",
    face: fonts.body,
    bold: true,
  });
  ctx.addText(slide, {
    text: String(pageNo).padStart(2, "0"),
    x: 1188,
    y: 676,
    w: 36,
    h: 22,
    fontSize: 14,
    color: "#64748b",
    face: fonts.mono,
    bold: true,
    align: "right",
  });
  return slide;
}

export function title(ctx, slide, text, y = 92, size = 29) {
  return ctx.addText(slide, {
    text,
    x: 76,
    y,
    w: 1128,
    h: 54,
    fontSize: size,
    color: C.ink,
    face: fonts.title,
    bold: true,
  });
}

export function subtitle(ctx, slide, text, y = 180) {
  return ctx.addText(slide, {
    text,
    x: 76,
    y,
    w: 1128,
    h: 34,
    fontSize: 14,
    color: C.muted,
    face: fonts.body,
  });
}

export function footer(ctx, slide, sourceText) {
  ctx.addShape(slide, { x: 58, y: 660, w: 1164, h: 1, fill: C.line });
  ctx.addText(slide, {
    text: `Source: ${sourceText}`,
    x: 76,
    y: 678,
    w: 980,
    h: 16,
    fontSize: 7.5,
    color: "#7890a8",
    face: fonts.body,
  });
}

export function panel(ctx, slide, { x, y, w, h, fill = C.white, stroke = C.line, title: heading, body, accent }) {
  ctx.addShape(slide, { x, y, w, h, fill, line: ctx.line(stroke, 1.4) });
  if (accent) ctx.addShape(slide, { x, y, w: 4, h, fill: accent });
  if (heading) {
    ctx.addText(slide, {
      text: heading,
      x: x + 18,
      y: y + 16,
      w: w - 36,
      h: 24,
      fontSize: 15,
      color: accent || C.ink,
      face: fonts.body,
      bold: true,
    });
  }
  if (body) {
    const bodyTop = y + (heading ? 48 : 18);
    const bottomPad = h > 90 ? 16 : 10;
    ctx.addText(slide, {
      text: body,
      x: x + 18,
      y: bodyTop,
      w: w - 36,
      h: h - (bodyTop - y) - bottomPad,
      fontSize: 10.5,
      color: C.muted,
      face: fonts.body,
    });
  }
}

export function pill(ctx, slide, { text, x, y, w, h = 28, fill = C.faint, stroke = C.line, color = C.ink }) {
  ctx.addShape(slide, { x, y, w, h, fill, line: ctx.line(stroke, 1) });
  const textHeight = h > 70 ? h - 26 : h - 6;
  ctx.addText(slide, {
    text,
    x: x + 12,
    y: y + 7,
    w: w - 24,
    h: textHeight,
    fontSize: 9.5,
    color,
    face: fonts.body,
    bold: true,
    align: "center",
  });
}

export function tinyLabel(ctx, slide, text, x, y, w, color = C.muted) {
  ctx.addText(slide, {
    text,
    x,
    y,
    w,
    h: 16,
    fontSize: 8.5,
    color,
    face: fonts.body,
    bold: true,
  });
}

export function arrow(ctx, slide, x, y, w, color = C.line) {
  ctx.addShape(slide, { x, y, w, h: 2, fill: color });
  ctx.addText(slide, {
    text: ">",
    x: x + w - 3,
    y: y - 11,
    w: 16,
    h: 24,
    fontSize: 16,
    color,
    face: fonts.mono,
    bold: true,
  });
}

export function row(ctx, slide, { x, y, w, h, fill, stroke, columns, texts, colors = [], bold = [] }) {
  ctx.addShape(slide, { x, y, w, h, fill, line: ctx.line(stroke, 1.2) });
  let left = x;
  const textTop = h < 32 ? y + 4 : y + 8;
  const textHeight = h < 32 ? h - 8 : h - 20;
  columns.forEach((cw, idx) => {
    if (idx > 0) ctx.addShape(slide, { x: left, y, w: 1, h, fill: stroke });
    ctx.addText(slide, {
      text: texts[idx],
      x: left + 12,
      y: textTop,
      w: cw - 24,
      h: textHeight,
      fontSize: idx === 0 ? 12 : 10,
      color: colors[idx] || C.ink,
      face: idx === 2 ? fonts.mono : fonts.body,
      bold: Boolean(bold[idx]),
    });
    left += cw;
  });
}
