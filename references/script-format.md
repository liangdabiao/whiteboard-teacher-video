# script.js 格式

一个视频项目的**唯一事实来源**：风格、口播、分页都在这里。画面（`pages/pNN.js`）按它的 `id` 对应。

## 完整结构

```js
(function (root) {
  const META = {
    style: 'whiteboard',        // 必填：study|whiteboard|chalkboard|warm-story|tech-dark
    title: '相对论入门',
    name: '相对论',              // 成片文件名（中文项目会生成「xx-无字幕.mp4」）
    gap: 0.5,                    // 页间停顿秒（引擎默认 1.5，有配音时用 0.3）
    // voice: { speaker: '...' }, // ftvoice.py 会自动写入 —— 写了引擎才加载 voice.js
    // lang: 'zh',               // 'en' 时成片文件名用英文（no-subtitles）
    // pace: { maxHold: 0.5 },   // 配音片的微调（松紧页间停顿）
    // libs: ['katex/dist/katex.min.css'],  // 第三方库（公式等）
    // extras: ['gauges.js'],    // 引用的组件（use-extra.mjs 会自动追加）
    // webgl: true,              // 页面用 three.js 时开
    // no: '3',                  // 页码（章节视频用）
  };

  const PAGES = [
    {
      id: 'p01',                  // 对应 pages/p01.js
      section: '开场',            // 左上角章节名，相���页相同会自动分组
      title: '第一页的标题',
      after: 0.5,                 // 讲完后再停一会儿（让画面沉一下再翻页）
      tail: 3,                    // 最后一页额外的停留
      cues: [                     // ★ 一条 cue = 一个动画锚点
        '第一句口播。',
        '第二句口播。',
        { t: '第三句，讲完多停一会儿。', hold: 0.6 },
      ],
      // sfx: [{ f: 'audio/blip.mp3', at: [0, 1.2], vol: -6 }],   // 音效（需自己准备文件）
    },
  ];

  root.SCRIPT = { META, PAGES };
})(typeof window !== 'undefined' ? window : globalThis);
```

## cue 的三种写法

| 写法 | 含义 |
|---|---|
| `'文本'` | 普通一句 |
| `{ t: '文本' }` | 同上 |
| `{ t: '文本', hold: 0.6 }` | 讲完后面多停 0.6 秒（画面继续动） |

## 约定

- **单句 ≤ 40 字**，太长配音会喘、画面跟不上
- **每页 2–3 句**，2–4 秒要有新东西出现
- **句尾带标点**：`。？！` 停顿 0.4s，`，、；：` 停顿 0.18s —— 这决定画面的呼吸节奏
- 页 id 形如 `p01` `p02`，对应 `pages/p01.js`
- `section` 相同的连续页会归为一个章节（左上角显示）

## 改稿后必须重跑配音

```bash
python scripts/ftvoice.py <项目>          # 全量（会跳过未变的句子）
python scripts/ftvoice.py <项目> --from 5 # 只重配第 5 条之后
```

`voice.js` 里的 `t` 字段必须和 cue 文本**逐字相同**——引擎靠它匹配（`timing.js:50`），不匹配就当这句没配音。

## voice.js（自动生成，不要手改）

```js
SCRIPT.VOICE = {
  speaker: 'Chinese (Mandarin)_Warm_Bestie',
  provider: 'apiz',
  pages: [[
    { t: '第一句口播。', f: 'audio/p01-c00-abc123.wav', d: 2.6, o: 0 },
    //  t = cue 文本（必须与 script.js 完全一致）
    //  f = 音频文件（相对项目目录）
    //  d = 该句真实时长（秒）
    //  o = 语音在段内的起点（逐句合成恒为 0）
    //  k = 字级 onset 数组（本 skill 不生成，P.cw 会按字数比例估算）
  ]],
};
```

## 时长怎么估

- 中文约 **4.3 字/秒**（引擎 `CPS`）
- 90 秒 ≈ 380 字 ≈ 7–9 页（每页 2–3 句）
- 配音后时长会**略短**（估算偏保守），实测差异约 5–10%

改了 cue 想知道实际多长：

```bash
node engine/tools/pages.mjs --json      # 每页起止 + 每句触发时刻
node engine/tools/pages.mjs             # 人类可读版
```