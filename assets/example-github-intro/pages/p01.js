/* p01 开场：左边一叠翻页的幻灯片（PPT 式），右边一块正在被画出来的白板。
 * 对比立住"不是翻页，是当场画"。 */
ENGINE.visual('p01', (P) => {
  const t0 = P.c(0), t1 = P.c(1), t2 = P.c(2);
  P.title('不是 PPT 翻页', { accent: 'blue' });

  // ══ 左：一叠幻灯片（PPT 式，整块翻过去）
  P.text('别人', { x: 300, y: 250, w: 200, align: 'c', size: 40, color: 'muted', at: t0, cps: 8 });
  [0, 1, 2].forEach((i) => {
    const off = (2 - i) * 22;
    P.box(220 + off, 320 + off, 500, 320, { color: 'soft', sw: 3.4, at: t0 + 0.2 + i * 0.25, dur: 0.45, texture: false });
  });
  // 最上面那张有"一张图"占位（整块淡入感）
  P.box(286, 386, 456, 200, { color: 'faint', sw: 2.6, at: t0 + 1.1, dur: 0.4, texture: false });
  P.text('整页一张图', { x: 514, y: 476, w: 456, align: 'c', size: 36, color: 'muted', at: t0 + 1.3, mode: 'fade', dur: 0.4 });
  // 翻页箭头
  P.arrow(760, 480, 900, 480, { color: 'soft', sw: 3.4, head: 20, at: t0 + 1.6, dur: 0.4 });

  // ══ 右：一块白板，笔正在画一个圆（一笔一笔）
  P.text('这个', { x: 1420, y: 250, w: 200, align: 'c', size: 40, color: 'blue', at: t1, cps: 8 });
  P.box(1090, 320, 660, 400, { color: 'ink', sw: 4, at: t1 + 0.2, dur: 0.6, texture: false });
  // 圆圈按笔画描出来
  P.circle(1420, 500, 220, { color: 'ink', sw: 6, at: t1 + 0.7, dur: 1.1 });
  // 笔
  P.line(1560, 380, 1600, 440, { color: 'ink', sw: 7, at: t2 - 0.2, dur: 0.2 });
  P.path('M1552 372 L1568 386 L1548 392 Z', { color: 'ink', fill: 'ink', sw: 2, at: t2 - 0.1, dur: 0.2 });
  P.text('一笔一笔画', { x: 1420, y: 760, w: 500, align: 'c', size: 38, color: 'blue', at: t2 + 0.2, cps: 9 });
});
