/* p06 全链路免费：四段流水线，每段一个图标 + 工具名 + 免费标记。 */
ENGINE.visual('p06', (P) => {
  const t0 = P.c(0), t1 = P.c(1), t2 = P.c(2);
  P.title('全链路免费', { accent: 'blue' });

  const steps = [
    { x: 200,  cn: '绘图', tool: 'PIL',       ic: 'puzzle' },
    { x: 640,  cn: '生图', tool: 'Agnes',     ic: 'sparkle' },
    { x: 1080, cn: '配音', tool: 'edge-tts',  ic: 'chat' },
    { x: 1520, cn: '合成', tool: 'ffmpeg',    ic: 'fuse' },
  ];
  const BW = 320, BH = 320, BY = 300;

  // 底部轨道
  P.line(200, BY + BH + 66, 1840, BY + BH + 66, { color: 'soft', sw: 3, at: t0, dur: 1.0 });

  steps.forEach((s, i) => {
    const t = t1 + i * 0.4;
    P.box(s.x, BY, BW, BH, { color: 'ink', sw: 4, at: t, dur: 0.45, texture: false });
    P.icon(s.ic, s.x + BW / 2, BY + 90, 100, { at: t + 0.3, dur: 0.4, color: 'ink' });
    P.text(s.cn, { x: s.x + BW / 2, y: BY + 150, w: BW, align: 'c', size: 46, color: 'ink', weight: 700, at: t + 0.5, cps: 8 });
    P.text(s.tool, { x: s.x + BW / 2, y: BY + 216, w: BW, align: 'c', size: 34, color: 'blue', at: t + 0.7, cps: 10 });
    P.text('免费', { x: s.x + BW / 2, y: BY + 264, w: BW, align: 'c', size: 32, color: 'green', at: t + 0.85, cps: 8 });
  });

  // 工序之间的箭头
  for (let i = 0; i < 3; i++) {
    const t = t1 + (i + 1) * 0.4 + 0.2;
    P.arrow(steps[i].x + BW + 12, BY + BH / 2, steps[i + 1].x - 12, BY + BH / 2,
      { color: 'soft', sw: 3.4, head: 18, at: t, dur: 0.35 });
  }

  // 底部
  P.text('一个字都不用手写，全部自动生成', { x: 960, y: 800, w: 1300, align: 'c', size: 40, color: 'ink', at: t2, cps: 10 });
});
