/* p06 结果：时间膨胀。两个钟，一个走得更慢。
 * 画面：两个并排的钟同时开始 → 上面的钟数字跳动间隔变长 → 强调「变慢」。 */
ENGINE.visual('p06', (P) => {
  P.title('时间膨胀', { accent: 'red' });
  const { clamp, ease } = PV;
  const t0 = P.c(0), t1 = P.c(1), t2 = P.c(2);

  const cy = 460;
  const clock = (x, at) => {
    P.circle(x, cy, 240, { color: 'ink', at, dur: 0.6, sw: 3.6 });
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * Math.PI * 2;
      P.line(x + Math.cos(a) * 96, cy + Math.sin(a) * 96,
             x + Math.cos(a) * 112, cy + Math.sin(a) * 112,
             { color: 'soft', at: at + 0.3 + i * 0.03, dur: 0.12, sw: 2 });
    }
  };

  // 左：站台上的钟（正常速度）
  const lx = 620, rx = 1300;
  clock(lx, t0);
  P.text('站台', { x: lx, y: 640, w: 280, align: 'c', size: 46, color: 'soft', at: t0 + 0.9, cps: 8 });

  // 右：飞快的人的钟（慢）
  clock(rx, t0 + 0.4);
  P.text('高速中的人', { x: rx, y: 640, w: 340, align: 'c', size: 46, color: 'soft', at: t0 + 1.2, cps: 9 });

  // 秒针速度对比：左边的秒针走得快，右边的慢
  P.liveRough((lt, R) => {
    const speedA = (lt - t1) * 3.0;   // 快
    const speedB = (lt - t1) * 1.1;   // 慢
    const a = speedA % (Math.PI * 2), b = speedB % (Math.PI * 2);
    return [
      R.line(lx, cy, lx + Math.cos(a - Math.PI / 2) * 88, cy + Math.sin(a - Math.PI / 2) * 88, { color: 'ink', sw: 3.4 }),
      R.line(rx, cy, rx + Math.cos(b - Math.PI / 2) * 88, cy + Math.sin(b - Math.PI / 2) * 88, { color: 'red', sw: 3.4 }),
    ];
  });

  // 强调：右边的钟变慢
  P.text('慢', { x: rx, y: 200, w: 200, align: 'c', size: 84, color: 'red', weight: 700, at: t1, cps: 5 });
  P.ring(rx, cy + 30, 250, 210, { color: 'red', at: t1 + 0.5 });

  // 累积效应（放在画面中上部，避开 y>905 的字幕带，也不被末尾的 push 影响）
  P.text('而且会累积', { x: 960, y: 730, w: 720, align: 'c', size: 48, color: 'ink', at: t2, cps: 10 });

  // 相机：只平移，不推近（push 会放大内容，导致下方文字溢出字幕带）
  P.cam([P.pan(t1, 1180, 500), P.back(P.endT - 0.4)]);
});