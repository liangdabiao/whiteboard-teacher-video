/* p01 开场：一列火车驶过站台，站台上有个人在看。
 * 白板风：黑笔主线，红笔只用于强调。逐笔画出，不用淡入。 */
ENGINE.visual('p01', (P) => {
  P.title('一个老问题', { accent: 'blue' });
  const { clamp } = PV;
  const t0 = P.c(0), t1 = P.c(1), t2 = P.c(2);

  // 地面线：一条横贯的轨道
  P.line(140, 700, 1780, 700, { color: 'soft', at: t0, dur: 1.2, sw: 3.2 });

  // 火车：车厢 + 车窗 + 轮子，从左驶向右
  // liveRough 的 R 只有 box/path/circle/line 四个方法，且直接返回 options 对象
  const trainY = 560;
  P.liveRough((lt, R) => {
    const k = clamp((lt - t0 - 0.1) / (P.endT - t0 - 0.6));
    const x = 40 + k * 620;
    const items = [R.box(x, trainY - 40, 620, 120, { r: 10, color: 'ink', sw: 3 })];
    for (let i = 0; i < 4; i++) {
      items.push(R.box(x + 52 + i * 140, trainY - 22, 96, 74, { r: 6, color: 'ink', sw: 2.4 }));
    }
    items.push(R.circle(x + 90, trainY + 96, 54, { color: 'ink', sw: 3 }));
    items.push(R.circle(x + 520, trainY + 96, 54, { color: 'ink', sw: 3 }));
    return items;
  });

  // 站台上的观察者：只画剪影，不画脸
  const px = 1280, py = 700;
  P.line(px - 200, py, px + 200, py, { color: 'soft', at: t1 - 0.6, dur: 0.5, sw: 2.6 });
  P.path(`M${px} ${py} v-150 M${px - 58} ${py - 96} h116 M${px - 56} ${py - 152} a56 56 0 0 1 112 0 z`,
    { color: 'ink', at: t1, dur: 0.8, sw: 3 });
  P.text('站台', { x: px, y: py + 20, w: 240, align: 'c', size: 40, color: 'muted', at: t1 + 0.5, cps: 10 });

  // 强调：速度线 + 问号
  for (let i = 0; i < 3; i++) {
    P.line(250 + i * 48, 440 + i * 28, 410 + i * 48, 440 + i * 28,
      { color: 'red', at: t2 + i * 0.12, dur: 0.22, sw: 2.6 });
  }
  P.text('高速', { x: 330, y: 408, w: 200, align: 'c', size: 56, color: 'red', weight: 700, at: t2 + 0.4, cps: 8 });
  P.text('?', { x: 1650, y: 360, size: 120, color: 'red', weight: 700, at: t2 + 0.7, cps: 4 });

  P.cam([P.pan(t1 + 0.4, 900, 570), P.back(P.endT - 0.3)]);
});