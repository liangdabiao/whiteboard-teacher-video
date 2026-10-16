/* p03 第二条公设：两条地基。
 * 画面：两块「地基」砖并排，逐条写上公设内容。红笔第一条，蓝笔第二条。 */
ENGINE.visual('p03', (P) => {
  P.title('两条地基', { accent: 'blue' });
  const t0 = P.c(0), t1 = P.c(1), t2 = P.c(2);

  // 地面线
  P.line(180, 740, 1740, 740, { color: 'soft', at: t0, dur: 0.9, sw: 3 });

  const brick = (x, label, color, txt, at) => {
    P.box(x, 540, 680, 190, { fill: color + 'F', color, at, dur: 0.8, r: 10, sw: 3.4 });
    P.text(label, { x: x + 40, y: 566, size: 52, color, weight: 700, at: at + 0.35, cps: 6 });
    P.text(txt, { x: x + 40, y: 634, size: 44, color: 'ink', at: at + 0.8, cps: 9 });
  };

  brick(220, '①', 'red', '所有人的光速都一样', t1);
  brick(1020, '②', 'blue', '没有绝对静止的参考系', t2);

  // 两条地基压住地面：底部小三角
  P.path('M260 730 l40 -34 l40 34 z', { color: 'red', at: t1 + 1.6, dur: 0.3, sw: 2.4 });
  P.path('M1060 730 l40 -34 l40 34 z', { color: 'blue', at: t2 + 1.8, dur: 0.3, sw: 2.4 });

  // 顶部一行：整栋楼要靠这两块撑住（把画面填满，也点明"地基"的含义）
  P.box(240, 300, 640, 150, { color: 'faint', at: t0 + 0.3, dur: 0.8, r: 10, sw: 2.6 });
  P.text('狭义相对论', { x: 560, y: 352, w: 400, align: 'c', size: 62, color: 'ink', weight: 700, at: t0 + 0.8, cps: 8 });
  P.arrow(560, 460, 560, 530, { color: 'soft', at: t1, dur: 0.4, sw: 2.6 });
  P.arrow(1360, 460, 1360, 530, { color: 'soft', at: t1 + 0.2, dur: 0.4, sw: 2.6 });

  P.cam([P.pan(t2, 1000, 620), P.back(P.endT - 0.3)]);
});