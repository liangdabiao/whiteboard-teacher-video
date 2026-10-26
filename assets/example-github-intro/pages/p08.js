/* p08 仓库：这是哪个 GitHub 项目、地址在哪 —— 每条片子必须有这一页。
 * whiteboard：黑笔框 + 蓝笔强调仓库名。 */
ENGINE.visual('p08', (P) => {
  const t0 = P.c(0), t1 = P.c(1);
  P.title('源码在这里', { accent: 'blue' });

  const REPO = 'whiteboard-explainer';
  const URL = 'https://github.com/liangdabiao/whiteboard-explainer';

  // ── 一块板书框
  P.box(240, 280, 1440, 400, { color: 'ink', sw: 4.5, at: t0, dur: 0.6, texture: false });
  P.text('github.com', { x: 1620, y: 300, w: 300, align: 'r', size: 26, color: 'muted', at: t0 + 0.5, mode: 'fade', dur: 0.3 });

  // ── 仓库名（大字，主角）
  P.text(REPO, { x: 960, y: 392, w: 1360, align: 'c', size: 76, color: 'blue', weight: 700, at: t0 + 0.7, cps: 10 });
  P.text('liangdabiao 的仓库', { x: 960, y: 512, w: 1200, align: 'c', size: 34, color: 'soft', at: t0 + 1.2, mode: 'fade', dur: 0.4 });

  // ── 完整地址（用下划线做"重点标记"的笔法）
  P.text(URL, { x: 960, y: 588, w: 1300, align: 'c', size: 34, color: 'ink', at: t1, cps: 24 });
  P.underline(310, 640, 1300, { color: 'blue', sw: 4, at: t1 + 1.0, dur: 0.5 });

  // ── 底部
  P.text('搜仓库名，或直接照地址敲', { x: 1060, y: 754, w: 900, align: 'c', size: 40, color: 'ink', at: t1 + 1.2, cps: 10 });
  P.icon('magnifier', 470, 778, 78, { color: 'blue', at: t1 + 1.4, dur: 0.35 });
});
