/* p02 第一条公设：地球在动，但光速量出来永远一样。
 * 画面：地球 + 轨道 → 两支等长的光箭 → 强调「一样快」 */
ENGINE.visual('p02', (P) => {
  P.title('光速不变', { accent: 'blue' });
  const { clamp, ease } = PV;
  const t0 = P.c(0), t1 = P.c(1), t2 = P.c(2), t3 = P.c(3), t4 = P.c(4);

  // ── 左：地球在转（椭圆轨道 + 地球 + 速度箭头）
  // ★ 地球是实心圆 + 轨道线，别只画轨道线（那看着像椭圆不像地球）
  const cx = 520, cy = 520;
  P.ellipse(cx, cy, 620, 320, { color: 'faint', at: t0, dur: 1.0, sw: 2.4 });
  P.circle(cx, cy, 190, { fill: 'blueF', color: 'blue', at: t0 + 0.4, dur: 0.7, sw: 3.2 });
  P.liveRough((lt, rough) => {
    const a = (lt - t0) * 0.55;
    const ex = cx + Math.cos(a) * 310, ey = cy + Math.sin(a) * 160;
    return [rough.circle(ex, ey, 64, { fill: 'orangeF', color: 'orange', sw: 3 })];
  });
  P.text('地球在动', { x: 560, y: 726, w: 300, align: 'c', size: 44, color: 'soft', at: t1, cps: 10 });

  // ── 中：分界线
  P.line(900, 240, 900, 800, { color: 'faint', at: t2, dur: 0.7, sw: 2.2 });

  // ── 右：两支光箭（不同方向，但一样长、一样快）
  P.text('不管光源怎么动', { x: 1320, y: 300, w: 480, align: 'c', size: 42, color: 'soft', at: t3, cps: 12 });
  P.arrow(1080, 430, 1560, 430, { color: 'red', at: t3 + 0.4, dur: 0.7, sw: 4 });
  P.text('3×10⁸ m/s', { x: 1320, y: 380, w: 400, align: 'c', size: 44, color: 'red', weight: 700, at: t3 + 0.9, cps: 8 });
  P.arrow(1560, 560, 1080, 560, { color: 'blue', at: t3 + 1.4, dur: 0.7, sw: 4 });
  P.text('3×10⁸ m/s', { x: 1320, y: 616, w: 400, align: 'c', size: 44, color: 'blue', weight: 700, at: t3 + 1.9, cps: 8 });

  // 两支箭同时到：右侧一条竖线标终点
  P.line(1570, 400, 1570, 600, { color: 'green', at: t4 - 0.5, dur: 0.4, sw: 3 });
  P.text('一样快', { x: 1330, y: 700, w: 320, align: 'c', size: 60, color: 'green', weight: 700, at: t4, cps: 6 });
  P.ring(1330, 730, 240, 84, { color: 'green', at: t4 + 0.7 });

  // 相机：只做轻微平移，不做 push（推镜会让边缘文字溢出画布，lint 会判 off-canvas）
  P.cam([P.pan(t3, 1350, 500), P.back(P.endT - 0.3)]);
});