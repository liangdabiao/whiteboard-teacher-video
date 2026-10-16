/* p04 矛盾：追光的船永远差一点点。
 * 画面：光箭 + 更快的船在后面追，两者之间的差距始终缩不到零。 */
ENGINE.visual('p04', (P) => {
  P.title('追不上的光', { accent: 'red' });
  const { clamp, ease } = PV;
  const t0 = P.c(0), t1 = P.c(1), t2 = P.c(2);

  // 光：一条长红线
  P.arrow(760, 300, 1740, 300, { color: 'red', at: t0 + 0.5, dur: 0.9, sw: 5 });
  P.text('光', { x: 1620, y: 236, size: 52, color: 'red', weight: 700, at: t0 + 1.0, cps: 6 });

  // 船：追光的人，速度比光慢一点点（liveRough：位置随时间推进但始终落后）
  P.liveRough((lt, R) => {
    const k = clamp((lt - t1) / Math.max(0.6, P.endT - t1));
    const bx = 300 + k * 980;
    return [
      R.box(bx, 520, 240, 120, { r: 10, color: 'ink', sw: 3.4 }),
      R.box(bx + 40, 452, 160, 66, { r: 8, color: 'soft', sw: 2.4 }),
    ];
  });
  P.text('追光的船', { x: 420, y: 672, w: 280, align: 'c', size: 46, color: 'ink', at: t1 + 0.2, cps: 9 });

  // 差距线：始终留缺口（这是全片的重点——差距缩不到零）
  P.liveRough((lt, R) => {
    const k = clamp((lt - t1 - 0.3) / Math.max(0.6, P.endT - t1 - 0.3));
    const bx = 300 + k * 980;
    const hx = 760 + k * 980;
    return [R.line(bx + 250, 560, hx - 10, 560, { color: 'muted', sw: 2.6, dashed: true })];
  });
  P.text('差一点', { x: 1330, y: 400, w: 280, align: 'c', size: 60, color: 'red', weight: 700, at: t2 - 0.6, cps: 6 });
  P.ring(1310, 430, 230, 90, { color: 'red', at: t2 - 0.2 });

  // 强调：差距永远不闭合
  P.text('?', { x: 1600, y: 660, size: 84, color: 'red', weight: 700, at: t2, cps: 4 });

  P.cam([P.push(t1 + 0.4, 900, 480, 1.08), P.back(P.endT - 0.3)]);
});