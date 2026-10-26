/* p04 两种模式：左=逐拍幻灯片（一拍一图，画面被外框框住、逐张翻），右=一张画布慢慢长满。 */
ENGINE.visual('p04', (P) => {
  const t0 = P.c(0), t1 = P.c(1), t2 = P.c(2);
  P.title('一拍一图，或一张画满', { accent: 'blue' });

  // 中缝分隔
  P.line(960, 240, 960, 830, { color: 'soft', sw: 2.4, dashed: true, at: t0, dur: 0.9 });

  // ══ 左：逐拍幻灯片 ══
  P.text('① 逐拍幻灯片', { x: 560, y: 240, w: 620, align: 'c', size: 42, color: 'ink', weight: 700, at: t0 + 0.3, cps: 9 });
  const slides = [
    { y: 320, txt: '一句话' },
    { y: 480, txt: '一张图' },
    { y: 640, txt: '再一句' },
  ];
  slides.forEach((s, i) => {
    const t = t1 + i * 0.45;
    P.box(260, s.y, 600, 128, { color: i === 1 ? 'blue' : 'ink', sw: 4, at: t, dur: 0.5, texture: false });
    P.text(s.txt, { x: 560, y: s.y + 36, w: 600, align: 'c', size: 40, color: i === 1 ? 'blue' : 'ink', at: t + 0.3, cps: 8 });
    if (i > 0) P.arrow(180, s.y - 20, 180, s.y + 48, { color: 'soft', sw: 3, at: t + 0.2, dur: 0.3, head: 14 });
  });

  // ══ 右：单画布生长 ══
  P.text('② 单画布生长', { x: 1420, y: 240, w: 720, align: 'c', size: 42, color: 'ink', weight: 700, at: t0 + 0.6, cps: 9 });
  // 一块大画布
  P.box(1090, 320, 660, 470, { color: 'ink', sw: 4, at: t1 + 0.2, dur: 0.6, texture: false });
  // 画布里的内容一块块长出来（越来越满）
  const grow = [
    [1140, 370, 180, 90], [1350, 370, 300, 60], [1140, 490, 260, 110],
    [1430, 460, 220, 150], [1140, 630, 520, 110],
  ];
  grow.forEach((g, i) => {
    const t = t2 + i * 0.22;
    P.box(g[0], g[1], g[2], g[3], { color: 'blue', sw: 3, at: t, dur: 0.4, texture: false });
  });
  P.text('整块板子慢慢长满', { x: 1420, y: 812, w: 760, align: 'c', size: 38, color: 'soft', at: t2 + 1.2, cps: 9 });
});
