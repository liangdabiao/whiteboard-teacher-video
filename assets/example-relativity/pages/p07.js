/* p07 真实世界：GPS 每天差 7 微秒。
 * 画面：地球 + 卫星轨道 → 强调 7 μs → 红色虚线表示地图偏移。 */
ENGINE.visual('p07', (P) => {
  P.title('GPS 每天差七微秒', { accent: 'orange' });
  const { clamp, ease } = PV;
  const t0 = P.c(0), t1 = P.c(1), t2 = P.c(2), t3 = P.c(3);

  // 地球
  const cx = 560, cy = 540;
  P.circle(cx, cy, 240, { fill: 'blueF', color: 'blue', at: t0, dur: 0.8, sw: 3.2 });

  // 卫星轨道 + 运动的卫星
  P.ellipse(cx, cy, 560, 220, { color: 'faint', at: t0 + 0.5, dur: 0.8, sw: 2.4 });
  P.liveRough((lt, R) => {
    const a = (lt - t0 - 0.5) * 0.7;
    const sx = cx + Math.cos(a) * 280, sy = cy + Math.sin(a) * 110;
    return [R.box(sx - 22, sy - 22, 44, 44, { r: 6, fill: 'orangeF', color: 'orange', sw: 3 })];
  });
  P.text('3.9 km/s', { x: 720, y: 700, w: 300, align: 'c', size: 44, color: 'orange', weight: 700, at: t1, cps: 9 });

  // 中间：每天 7 微秒（红笔强调）
  // ★ 分隔线把「数字区」和「地图区」分开；荧光笔只垫在数字下方一小条，绝不压字
  P.line(1000, 280, 1000, 800, { color: 'faint', at: t1 + 0.3, dur: 0.6, sw: 2.2 });
  P.text('每天', { x: 1260, y: 300, w: 400, align: 'c', size: 44, color: 'soft', at: t1 + 0.5, cps: 8 });
  P.text('7 微秒', { x: 1260, y: 380, w: 440, align: 'c', size: 80, color: 'red', weight: 700, at: t2 - 0.3, cps: 6 });
  P.mark(1070, 452, 380, 40, { at: t2, dur: 0.4 });

  // 右：不修的话地图会偏出公里（放在右下，与左侧数字区不重叠）
  const mx = 1420, my = 640;
  P.box(mx - 170, my - 150, 340, 230, { color: 'ink', at: t2 + 0.4, dur: 0.7, sw: 3 });
  P.path(`M${mx - 120} ${my - 40} q 60 -52 112 -8 q 52 42 112 -26`,
    { color: 'green', at: t2 + 1.0, dur: 0.6, sw: 3.4 });
  P.path(`M${mx - 120} ${my - 10} q 68 -34 120 8 q 52 42 112 -18`,
    { color: 'red', at: t2 + 1.5, dur: 0.6, sw: 3.4, dashed: true });
  P.text('正确路线', { x: mx, y: my + 108, w: 300, align: 'c', size: 38, color: 'green', at: t2 + 2.1, cps: 9 });
  P.text('偏出公里', { x: mx, y: my + 162, w: 300, align: 'c', size: 38, color: 'red', at: t3, cps: 9 });

  P.cam([P.push(t2, 1240, 480, 1.12), P.back(P.endT - 0.4)]);
});