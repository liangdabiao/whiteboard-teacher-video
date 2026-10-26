/* p02 真手绘：图形按笔画描出、文字逐笔写出。
 * 白板风：黑笔为主，一支蓝笔做强调。 */
ENGINE.visual('p02', (P) => {
  const t0 = P.c(0), t1 = P.c(1), t2 = P.c(2);
  P.title('图形一笔笔描出来', { accent: 'blue' });

  // ── 一支笔（右上），笔尖朝下
  P.line(1560, 230, 1560, 300, { color: 'ink', sw: 6, at: t0, dur: 0.20 });
  P.path('M1540 300 L1580 300 L1560 340 Z', { color: 'ink', fill: 'ink', sw: 3, at: t0 + 0.2, dur: 0.2 });
  P.text('笔尖', { x: 1650, y: 300, w: 200, align: 'c', size: 34, color: 'blue', at: t0 + 0.5, cps: 8 });

  // ── 房子（分三笔画出来：屋顶、墙体、门）
  // 第 1 笔：屋顶
  P.path('M480 420 L700 280 L920 420', { color: 'ink', sw: 5, at: t0 + 0.3, dur: 0.9 });
  P.text('第 1 笔', { x: 300, y: 330, w: 240, align: 'c', size: 34, color: 'soft', at: t0 + 0.5, cps: 8 });
  // 第 2 笔：墙
  P.path('M520 420 L520 660 L880 660 L880 420', { color: 'ink', sw: 5, at: t1, dur: 1.0 });
  P.text('第 2 笔', { x: 300, y: 540, w: 240, align: 'c', size: 34, color: 'soft', at: t1 + 0.2, cps: 8 });
  // 第 3 笔：门
  P.path('M660 660 L660 540 L740 540 L740 660', { color: 'blue', sw: 5, at: t2, dur: 0.6 });
  P.text('第 3 笔', { x: 300, y: 640, w: 240, align: 'c', size: 34, color: 'blue', at: t2 + 0.1, cps: 8 });

  // ── 右侧：逐笔写出的字
  P.text('手绘', { x: 1300, y: 470, w: 400, align: 'c', size: 96, color: 'ink', weight: 700, at: t1 + 0.6, cps: 5 });
  P.text('不是整块淡入', { x: 1300, y: 620, w: 420, align: 'c', size: 38, color: 'soft', at: t2, cps: 9 });
});
