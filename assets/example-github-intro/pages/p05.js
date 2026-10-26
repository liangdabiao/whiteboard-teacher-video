/* p05 本地 CPU：云端那条路打叉，本机 CPU 这条路走通；改一句重渲一秒。 */
ENGINE.visual('p05', (P) => {
  const t0 = P.c(0), t1 = P.c(1), t2 = P.c(2);
  P.title('本地 CPU，零 API 成本', { accent: 'blue' });

  // ══ 左：云端那条路（打叉）
  P.text('云端接口', { x: 480, y: 300, w: 380, align: 'c', size: 40, color: 'soft', at: t0, cps: 8 });
  // 云朵
  P.path('M360 470 C310 470 290 430 320 400 C310 360 360 330 400 350 C420 310 490 310 510 350 C560 340 590 380 570 410 C600 440 570 480 530 480 Z',
    { color: 'soft', sw: 4, at: t0 + 0.3, dur: 0.9 });
  P.text('要花钱', { x: 450, y: 540, w: 300, align: 'c', size: 36, color: 'red', at: t0 + 1.0, cps: 8 });
  P.text('会限流', { x: 450, y: 600, w: 300, align: 'c', size: 36, color: 'red', at: t0 + 1.3, cps: 8 });
  P.cross(450, 415, 220, { color: 'red', sw: 6, at: t1, dur: 0.5 });

  // ══ 右：本机 CPU（走通）
  P.text('你自己的电脑', { x: 1420, y: 300, w: 520, align: 'c', size: 40, color: 'ink', at: t1, cps: 8 });
  P.icon('cpu', 1420, 470, 300, { at: t1 + 0.3, dur: 0.9, color: 'blue' });
  P.text('不花钱', { x: 1420, y: 680, w: 320, align: 'c', size: 38, color: 'green', at: t1 + 1.1, cps: 8 });
  P.check(1600, 720, 70, { color: 'green', sw: 6, at: t1 + 1.4, dur: 0.4 });

  // ══ 中间箭头（从云端划掉 → 转向本机）
  P.arrow(760, 470, 1180, 470, { color: 'blue', sw: 4, bend: -0.12, head: 22, at: t1 + 0.6, dur: 0.7 });

  // ══ 底部：改一句重渲一秒
  P.text('改一句，重渲一秒', { x: 960, y: 800, w: 900, align: 'c', size: 44, color: 'blue', at: t2, cps: 9 });
});
