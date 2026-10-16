/* p08 收束：火车驶离，剩下光独自射出。
 * 收尾落在「物体的动作」上，不落在金句卡上。 */
ENGINE.visual('p08', (P) => {
  P.title('光说了算', { accent: 'blue' });
  const { clamp } = PV;
  const t0 = P.c(0), t1 = P.c(1);

  // 地面线
  P.line(140, 660, 1780, 660, { color: 'soft', at: t0, dur: 0.9, sw: 3 });

  // 火车加速驶出画面
  P.liveRough((lt, R) => {
    const k = clamp((lt - t0 - 0.2) / Math.max(1, P.endT - t0 - 1.2));
    const x = 180 + k * k * 1700;      // 二次加速
    const items = [R.box(x, 560, 380, 110, { r: 10, color: 'muted', sw: 2.6 })];
    for (let i = 0; i < 2; i++) {
      items.push(R.box(x + 34 + i * 108, 574, 72, 56, { r: 6, color: 'faint', sw: 2 }));
    }
    return items;
  });

  // 只剩光：一条向前的光箭（画满内容区，收尾落在动作上）
  P.arrow(180, 290, 1740, 290, { color: 'orange', at: t1, dur: 1.1, sw: 6 });
  P.text('光说了算', { x: 960, y: 180, w: 520, align: 'c', size: 72, color: 'orange', weight: 700, at: t1 + 0.4, cps: 8 });

  // 速度感留白：短横线三组
  for (let i = 0; i < 3; i++) {
    P.line(220 + i * 40, 400 + i * 34, 320 + i * 40, 400 + i * 34,
      { color: 'faint', at: t1 + 0.8 + i * 0.1, dur: 0.2, sw: 2.2 });
  }
  for (let i = 0; i < 3; i++) {
    P.line(1100 + i * 44, 430 + i * 30, 1210 + i * 44, 430 + i * 30,
      { color: 'faint', at: t1 + 1.1 + i * 0.1, dur: 0.2, sw: 2.2 });
  }

  // 结尾落点：光带走的一句，脚注式小字（不占主视觉）
  P.line(300, 790, 1620, 790, { color: 'faint', at: t1 + 1.4, dur: 0.6, sw: 2 });
  P.text('时间与空间，都由光来丈量', { x: 960, y: 812, w: 700, align: 'c', size: 44, color: 'soft', at: t1 + 1.6, cps: 12 });

  P.cam([P.back(P.endT - 0.3, 960, 460, 1.0)]);
});