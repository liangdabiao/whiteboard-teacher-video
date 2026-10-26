/* 白板手绘讲解视频：whiteboard-explainer
 * 目标 ~70 秒 · whiteboard 白板风 · 贯穿意象：一支笔在板上画
 * 纪律：一页一观点；每页 2-3 句；单句 ≤ 40 字；句尾带标点。
 */
(function (root) {
  const META = {
    voice: { speaker: 'zh-CN-XiaoxiaoNeural' },   // ← 由 ftvoice.py 自动写入，手写时可删
    style: 'whiteboard',
    title: '白板手绘讲解视频：whiteboard-explainer',
    name: 'whiteboard-explainer',                 // 成片文件名前缀
    gap: 0.5,
  };
  const PAGES = [
    { id: 'p01', section: '开场', title: '不是 PPT 翻页', cues: [
      '别人的讲解视频，是一页页图片翻过去。',
      '这个不一样：',
      { t: '它是一笔一笔，当场画出来的。', hold: 0.5 },
    ] },
    { id: 'p02', section: '真手绘', title: '图形一笔笔描出来', cues: [
      '图形按笔画描出，文字逐笔写出。',
      '不是整块淡入，',
      { t: '你能看见笔尖走完全程。', hold: 0.5 },
    ] },
    { id: 'p03', section: '音画对齐', title: '讲到哪，画到哪', cues: [
      '更关键的是对齐。',
      '旁白讲到月亮，月亮就在那一刻画出来。',
      { t: '元素级对齐，不是整页对齐。', hold: 0.5 },
    ] },
    { id: 'p04', section: '两种模式', title: '一拍一图，或一张画满', cues: [
      '它有两种成片模式。',
      '一种是逐拍幻灯片：一拍一张图，适合逐句讲解。',
      { t: '另一种是一张画布慢慢长满，适合推导和流程图。', hold: 0.5 },
    ] },
    { id: 'p05', section: '渲染', title: '本地 CPU，零 API 成本', cues: [
      '渲染在你自己电脑上跑。',
      '不用调云端接口，所以不花钱、也不怕限流。',
      { t: '一帧一帧算出来，改一句，重渲一秒。', hold: 0.5 },
    ] },
    { id: 'p06', section: '工具链', title: '全链路免费', cues: [
      '整条工具链都是免费的。',
      '绘图、生图、配音、合成，四段各用各的免费方案。',
      { t: '一个字都不用手写。', hold: 0.5 },
    ] },
    { id: 'p07', section: '收束', title: '适合谁', cues: [
      '知识科普、数学推导、流程讲解，都合适。',
      '要的是手绘感，',
      { t: '又要能精确重渲，就选它。', hold: 0.8 },
    ] },
    { id: 'p08', section: '仓库', title: '源码在这里', cues: [
      '这是它的 GitHub 仓库，liangdabiao 下的 whiteboard-explainer。',
      { t: '搜仓库名，或者直接照地址敲，就能找到。', hold: 1.2 },
    ] },
  ];
  root.SCRIPT = { META, PAGES };
})(typeof window !== 'undefined' ? window : globalThis);
