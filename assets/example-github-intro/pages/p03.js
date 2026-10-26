/* p03 音画对齐：旁白讲到"月亮"，月亮就在那一刻画出来（元素级对齐）。 */
ENGINE.visual('p03', (P) => {
  const t0 = P.c(0), t1 = P.c(1), t2 = P.c(2);
  P.title('讲到哪，画到哪', { accent: 'blue' });

  // ── 上方：旁白时间轴（一条线 + 三句刻度）
  P.line(240, 300, 1680, 300, { color: 'soft', sw: 3, at: t0, dur: 0.8 });
  const cues = ['太阳', '月亮', '挡住'];
  cues.forEach((w, i) => {
    const x = 520 + i * 320;
    P.line(x, 278, x, 322, { color: 'soft', sw: 3, at: t0 + 0.4 + i * 0.15, dur: 0.2 });
    P.text(w, { x, y: 214, w: 200, align: 'c', size: 34, color: 'soft', at: t0 + 0.5 + i * 0.15, cps: 8 });
  });
  P.text('旁白', { x: 300, y: 258, w: 160, align: 'c', size: 32, color: 'muted', at: t0 + 0.3, mode: 'fade', dur: 0.3 });

  // ── 太阳（第 1 句开始画）
  P.circle(620, 590, 200, { color: 'orange', sw: 5, at: t0 + 0.2, dur: 0.8 });
  [0, 1, 2, 3, 4, 5, 6, 7].forEach((i) => {
    const a = (i / 8) * Math.PI * 2;
    P.line(620 + Math.cos(a) * 118, 590 + Math.sin(a) * 118, 620 + Math.cos(a) * 156, 590 + Math.sin(a) * 156,
      { color: 'orange', sw: 4, at: t0 + 0.9 + i * 0.07, dur: 0.2 });
  });
  P.text('太阳', { x: 620, y: 730, w: 240, align: 'c', size: 40, color: 'ink', at: t0 + 1.1, cps: 8 });

  // ── 月亮：念到"月亮"那一刻才画（关键：P.cw）
  const tm = P.cw(1, '月亮', 0.1);
  P.path('M1240 500 A110 110 0 1 0 1240 680 A88 88 0 1 1 1240 500 Z',
    { color: 'blue', sw: 5, at: tm, dur: 0.9 });
  P.text('月亮', { x: 1240, y: 730, w: 240, align: 'c', size: 40, color: 'ink', at: tm + 0.2, cps: 8 });
  // 高亮：月亮这条刻度和月牙之间连一条虚线
  P.line(1160, 322, 1210, 480, { color: 'blue', sw: 2.4, dashed: true, at: tm, dur: 0.5 });

  // ── 底部结论
  P.text('元素级对齐，不是整页对齐', { x: 960, y: 812, w: 1100, align: 'c', size: 40, color: 'blue', at: t2 + 0.2, cps: 10 });
});
