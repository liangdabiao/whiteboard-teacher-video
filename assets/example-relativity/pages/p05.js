/* p05 解法：同时不再同时。
 * 画面：中点一次闪光 → 光向两边传 → 两个钟收到的时间不一样。 */
ENGINE.visual('p05', (P) => {
  P.title('同时不再同时', { accent: 'blue' });
  const { clamp, ease } = PV;
  const t0 = P.c(0), t1 = P.c(1), t2 = P.c(2);

  // 轨道上的两个点：A（左）和 B（右）
  // ⚠️ 变量名不要用 R —— liveRough 的第二个参数就是 rough 对象，遮蔽会导致坐标全变 NaN
  const xL = 520, xR = 1400, Y = 560;
  P.line(xL - 160, Y, xR + 160, Y, { color: 'soft', at: t0, dur: 1.0, sw: 3 });
  P.line(xL, Y - 70, xL, Y + 70, { color: 'ink', at: t0 + 0.6, dur: 0.3, sw: 3 });
  P.line(xR, Y - 70, xR, Y + 70, { color: 'ink', at: t0 + 0.7, dur: 0.3, sw: 3 });
  P.text('A', { x: xL, y: Y - 120, w: 120, align: 'c', size: 56, weight: 700, at: t0 + 0.9, cps: 5 });
  P.text('B', { x: xR, y: Y - 120, w: 120, align: 'c', size: 56, weight: 700, at: t0 + 1.0, cps: 5 });

  // 两个钟（A 和 B 各一个）
  const clock = (x, y, at) => {
    P.circle(x, y, 110, { color: 'ink', at, dur: 0.5, sw: 3 });
    P.line(x, y, x, y - 36, { color: 'ink', at: at + 0.3, dur: 0.2, sw: 2.6 });
    P.line(x, y, x + 26, y + 12, { color: 'ink', at: at + 0.4, dur: 0.2, sw: 2.6 });
  };
  clock(xL, Y + 170, t1 - 0.8);
  clock(xR, Y + 170, t1 - 0.6);

  // 中点的一次闪光（圆 + 八条光芒，不用圆弧 path）
  const M = (xL + xR) / 2;
  P.liveRough((lt, rough) => {
    const age = lt - t1;
    if (age < 0) return null;
    const r = Math.min(300, age * 620);
    const items = [rough.circle(M, Y, r * 2, { color: 'orange', sw: 3 })];
    // 光芒：8 条短线，长度随 r 增长
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * Math.PI * 2 + 0.4;
      const r0 = r + 8, r1 = r + 8 + Math.min(26, r * 0.18);
      items.push(rough.line(M + Math.cos(a) * r0, Y + Math.sin(a) * r0,
                            M + Math.cos(a) * r1, Y + Math.sin(a) * r1,
                            { color: 'orange', sw: 2.6 }));
    }
    return items;
  });
  P.text('一次闪光', { x: M, y: 250, w: 320, align: 'c', size: 48, color: 'orange', weight: 700, at: t1, cps: 8 });

  // 光向两边扩散（两道传播波前）
  P.liveRough((lt, rough) => {
    const age = lt - t1;
    if (age < 0) return null;
    const d = Math.min(520, age * 700);
    return [
      rough.line(M - d, Y - 120, M - d, Y + 120, { color: 'orange', sw: 2.4 }),
      rough.line(M + d, Y - 120, M + d, Y + 120, { color: 'orange', sw: 2.4 }),
    ];
  });

  // 结果：左钟先响，右钟后响 → 不再「同时」
  P.text('同时？', { x: M, y: 720, w: 320, align: 'c', size: 52, color: 'red', weight: 700, at: t2 - 0.9, cps: 8 });
  // ★ cross/check 的第三参数是「尺寸」，不是配置对象：P.cross(x, y, 尺寸, { 配置 })
  P.cross(M + 10, 716, 64, { color: 'red', at: t2 - 0.4 });

  P.cam([P.push(t1, M, 520, 1.12), P.back(P.endT - 0.4)]);
});