/* p07 收束：三个适用场景 + 一句结论（落在"笔继续画"的动作上，不是金句卡）。 */
ENGINE.visual('p07', (P) => {
  const t0 = P.c(0), t1 = P.c(1), t2 = P.c(2);
  P.title('适合谁', { accent: 'blue' });

  // ── 三个场景卡
  const cards = [
    { x: 200, cn: '知识科普', ic: 'bulb' },
    { x: 720, cn: '数学推导', ic: 'books' },
    { x: 1240, cn: '流程讲解', ic: 'gear' },
  ];
  cards.forEach((c, i) => {
    const t = t0 + i * 0.4;
    P.box(c.x, 290, 480, 240, { color: 'ink', sw: 4, at: t, dur: 0.45, texture: false });
    P.icon(c.ic, c.x + 240, 380, 96, { at: t + 0.3, dur: 0.4, color: 'ink' });
    P.text(c.cn, { x: c.x + 240, y: 448, w: 480, align: 'c', size: 44, color: 'ink', weight: 700, at: t + 0.5, cps: 8 });
  });

  // ── 两个条件（要手绘感 + 能精确重渲）
  P.check(250, 600, 76, { color: 'green', sw: 6, at: t1, dur: 0.4 });
  P.text('要手绘感', { x: 320, y: 590, size: 44, color: 'ink', at: t1 + 0.1, cps: 8 });

  P.check(950, 600, 76, { color: 'green', sw: 6, at: t1 + 0.4, dur: 0.4 });
  P.text('又要能精确重渲', { x: 1020, y: 590, size: 44, color: 'ink', at: t1 + 0.5, cps: 8 });

  // ── 结论落在"继续画"的动作：一条正在画的线 + 箭头
  const tEnd = P.cw(2, '选它', 0.1);
  P.line(300, 760, 1100, 760, { color: 'blue', sw: 6, at: tEnd, dur: 0.6 });
  P.arrow(1100, 760, 1320, 760, { color: 'blue', sw: 6, head: 26, at: tEnd + 0.5, dur: 0.35 });
  P.text('就选它', { x: 1480, y: 726, w: 360, align: 'c', size: 56, color: 'blue', weight: 700, at: tEnd + 0.7, cps: 8 });
});
