---
name: whiteboard-teacher-video
version: 1.0.0
display_name: 手绘讲解视频
display_name_en: Whiteboard Teacher Video
description: 图文讲解视频 skill：把知识讲解/科普/推导/开源项目介绍做成「手绘会动的画面」讲解视频——图形由代码逐笔绘出、文字逐字写出、讲到哪画到哪（音画对齐）。五套风格可选（白板/黑板/书卷/暖色插画/科技深色），29 个现成组件（图表、流程、仪表、终端、3D），本地 Chrome 渲染、零生图 API 成本、任何改动秒级重渲。当用户要做知识讲解视频、概念科普、图解动画、GitHub 项目介绍片，或要求「手绘动画」「讲动画」「图文视频」「explainer」「animación」时使用。触发词：讲解视频、科普视频、图解视频、手绘动画、讲动画、逐笔绘制、图文并茂的视频、项目介绍视频、开源项目介绍、skill 介绍片、GitHub 项目视频、explainer video、whiteboard teacher。
description_zh: 把讲解稿变成「手绘会动的画面」讲解视频。图形由代码逐笔绘出、文字逐字写出、讲到哪画到哪，五套风格可选，本地 Chrome 渲染，零生图 API 成本，改动秒级重渲。适合知识讲解、概念科普、图解动画与课程视频。
description_en: Turn a script into a whiteboard-style explainer video where every shape is drawn by code, word by word, exactly when it is spoken. Five visual styles, 29 built-in components, rendered locally in Chrome with zero image-generation API cost, and re-renders in seconds after any edit. Best for concept explainers, science communication, animated diagrams, and course videos.
---

# Whiteboard Teacher Video · 图文讲解视频

把讲解稿变成一支会「自己画出来」的讲解视频。画面不是生成图片，而是**代码逐笔绘制**——所以可重渲、可精修、零生图成本。

## 引擎契约（先理解这一条）

**整片是时间的纯函数。** `ENGINE.renderAt(t)` 渲染第 `t` 秒的画面，与之前播放过什么无关。

由此得到四个能力，也是你必须遵守纪律的**根本原因**：

| 能力 | 靠什么 |
|---|---|
| 改一页只重渲受影响片段 | 分段缓存 key = sha1(引擎 + 该页代码) |
| 12 个浏览器并行渲染 | 各段互不依赖 |
| 预览可瞬移到任意时刻 | 无需从头播放 |
| 确定性校验 | 同一时刻渲染两次比对像素 |

**红线：页面代码禁止 `Math.random()` / `Date.now()` / CSS transition / rAF。** 随机必须走 `PV.rng(seed)`，时间一律用 `P.c(i)` / `P.cw(i,'词')`。破坏这条，上面四个能力全部失效。

## 工作流（照着走，不要跳步）

```
用户："做一个讲相对论的 90 秒视频"
  ↓
① 读 references/storyboard-method.md → 写 storyboard.json
② ★★★ 停下来，把分镜念给用户确认 ★★★   ← 唯一强制人类闸门
③ 写 script.js（口播，按分镜填 cue）
④ python scripts/ftnew.py <项目> --title "..." --style whiteboard
⑤ python scripts/ftvoice.py <项目>        → voice.js + 字幕.srt
⑥ 逐页写 pages/pNN.js                      ← 主要创作量
⑦ python scripts/ftcheck.py <项目>         → lint + 每页拼图
⑧ 用 Read 打开 out/snap/pNN.jpg 逐页看图   → 定点修，**别超过 2 轮**
⑨ python scripts/ftrender.py --fps 24 --skip-subs   → **先出一个能看的粗片**
⑩ ★ 交付粗片给用户 ★                     ← 不要攒着不交付
⑪ 看图修一轮 → ftrender.py                → 交付正式版
```

**第 ② 步不可跳过。** 分镜错了，后面画得再好看也是一份幻灯片。原项目把这条做成 promise 闸门是有原因的。

### 配音后端

默认 `edge`（免费、无需 API key）；付费备选用 `apiz`：

```bash
python scripts/ftvoice.py <项目> --backend edge --voice mature --speed 1.15
```

edge 的旧域名（`speech.platform.bing.com`）在 2026 年起很多地区 403；
`scripts/edge_tts_speak.py` 已自动改走 `api.msedgeservices.com`，失败再回退旧域名。
不需要 `edge-tts` CLI。先跑 `--probe`，细节见 `references/tts-backends.md`。

### ★★ 第 ⑩ 步同样重要：先出片，再打磨

**用户要的是视频，不是完美的视频。** 交付节奏比成品精度更重要。

- **第 ⑧ 步的质检修到「不出现明显错误」就够**（lint 无 error、文字没被盖住、NaN 为 0），**不要追求构图完美**
- 第一次渲染用 `--fps 24 --skip-subs`（快 40%），先给用户一个能看的版本
- **不要把所有轮次修完再交付**。用户看到粗片才能给出真正的反馈
- 想改风格、加页、调内容？**改完重渲就行**，分段缓存会让第二轮很快（实测改单页 1 分钟）

> **实测教训**：做那条 95 秒 8 页的片子时，我在「lint 报的问题值不值得改」上反复纠结了两轮才交付，用户等得不耐烦。
> **正确做法**：lint error 修掉、明显 bug 修掉，粗片先出去，剩下的一轮里改。

### ★ lint 全绿 ≠ 画面是对的

`lint` 是机器检查，只能查出界/重叠/字号这类硬错误；**构图好不好、元素挤不挤、文字有没有被色块盖住，只有看图才知道**。

> **实测教训**：p07 那一页 lint 报 0 错误、质检显示全绿，但看拼图发现「7 微秒」的"微秒"被荧光笔完全盖住，只剩红色的「7」——观众完全读不出单位。

## 硬纪律

### ★ 节奏（最重要的一条）

- **用户要的是视频，不是完美的视频。** 粗片也是片，攒着不交付等于没做
- **质检修到「不出明显错误」就停**，不要追求构图完美
- **第一次渲染用 `--fps 24 --skip-subs`**（快 40%），先把能看的版本交出去
- 改一轮再交正式版。分段缓存让第二轮很快（实测改单页 1 分钟）

### 画面
- **内容区**：x 140–1780，y 180–880。y > 900 是字幕带，**不许放内容**
- **★ 文字居中必须给 `w` + `align:'c'`** —— 不给 `w` 时 `x` 是**左边缘**不是中心，这是最高频的错
- **★ 有 `P.push()` 的页面，元素往画面中间放** —— 推镜放大后边缘文字会溢出画布（lint 报 off-canvas）
- **正文字号 ≥ 32px**（< 24px 会被 lint 判失败）
- **每屏中文字 ≤ 8 个字**
- **配色只写语义名**：`ink` `soft` `muted` `faint` `blue` `orange` `red` `green` `purple` `yellow`，加 `F` 是浅填充（`blueF`）。**不许硬编码 hex**——写错名字引擎会记下来由质检报告
- **一页一观点**，2–3 句口播，2–4 秒要有新东西出现

### 动画
- `P.c(i, dt)` = 第 i 句开始 + dt 秒
- `P.cw(i, '词', dt)` = 第 i 句**念到某词** + dt 秒（关键数字用这个：数字刚好被念到就出现）
- `P.ce(i)` = 该句结束；`P.endT` = 本页讲完
- 强调用笔法（`ring` 圈 / `underline` 下划线 / `mark` 荧光笔 / `cross` 叉 / `check` 勾），不靠特效
- 翻页瞬间页面上**必须有东西**，不能空白

## 迭代
- 改单页 → 只重渲那页（`ftcheck.py --only pNN`），不要全量
- **lint 有 error 就别渲染**，先修
- **lint 过了也要看拼图** —— lint 只管硬错误，好不好看、盖没盖住它不管
- `ftcheck.py` 会报 **NaN** —— 那是 lint 查不到的致命伤（图形静默消失）
- 修不完就标「需要关注」并继续，**不要卡死**（**最多 2 轮就该出片**）

### 参考耗时（本机实测，8 页 87 秒片子）

| 阶段 | 耗时 |
|---|---|
| 建项目 + 写 8 页画面代码 | 约 10 分钟（人的创作时间） |
| 配音 26 句 | 约 1.5 分钟 |
| 质检（lint + 8 页拼图） | 约 1 分钟 |
| 渲染（首次，12 worker） | 约 2 分 45 秒 |
| 渲染（改单页后，缓存命中） | **约 1 分钟** |
| 渲染（`--fps 24 --skip-subs` 快版） | 约 1 分 40 秒 |

**所以从建项目到出第一条片，全程约 15 分钟。** 迭代单页一分钟——所以不必攒着改完再交付。

### 引擎 API 的三个高频坑

```js
// ① 文字居中：不给 w 时 x 是左边缘，不是中心
P.text('站台', { x: 420, y: 640, w: 280, align: 'c', size: 46 });   // ✓ 中心在 420

// ② check/cross 的第三参数是「尺寸」，不是配置对象（传错只刷 NaN，不报错）
P.cross(970, 716, 64, { color: 'red', at: t });   // ✓
P.cross(970, 716, { color: 'red', at: t });      // ✗ sz = [object Object]

// ③ liveRough 的回调参数别叫 R；且 R 只有 box/circle/line/path 四个方法
const R = 1400;                                    // ← 会被回调参数覆盖
P.liveRough((lt, R) => (xL + R) / 2);              // ✗ NaN
P.liveRough((lt, rough) => [rough.box(x, y, w, h, { color: 'ink' })]);  // ✓
```

**渲染时留意控制台的 `NaN`** —— 它不抛异常、lint 也不一定报，但对应图形就是画不出来。

完整清单见 `references/page-api.md`。

## 能做 / 不能做

**能**：知识科普、概念解释、流程推导、数据图表讲解、产品演示（可嵌真实截图）、GitHub 项目讲解；五套风格；横屏/竖屏；中英配音；自动字幕；20 秒到 10 分钟。

> **做 GitHub 项目 / skill 介绍片时，先读 `references/github-project-intro.md`。**
> 这类片子有硬要求：**最后一页必须是仓库地址页**（仓库名大字 + 完整 URL + owner + 怎么找），
> 否则观众看完不知道项目叫什么、去哪找 —— 片子等于白做。仓库名要从原文原样复制，
> **不能按文件名 slug 推断**（实测 `ai-data-hub.md` 的仓库其实是 `AI_data_hub`）。

**不能**：
- 写实照片/三维实拍风格（要那种质感请用生图工具）
- 自动配乐与音效床（`page.sfx` 能做，但要自己准备音频文件）
- 生图式的手绘插画（组件都是代码画的矢量图）
- 一次生成几十页（每页都要写代码，建议 ≤ 12 页）

## 与 whiteboard-explainer 的区别

| | whiteboard-explainer | **frametell-video（本 skill）** |
|---|---|---|
| 画面 | 像素级笔画生长 | rough.js 风格化绘制 |
| 风格 | 单一（白板，底色硬编码） | **五套，含深色** |
| 组件 | 全部手写 | **29 个现成** |
| 质检 | 归属检查 | lint + 拼图 + 确定性 |
| 适合 | 数学推导、强手绘感 | 科普讲解、图表密集、多风格 |

需要「真手绘感 / 逐元素生长」→ 用 whiteboard-explainer。需要「多风格 / 复杂图表 / 组件复用 / 强质检」→ 用本 skill。

## 文档索引

| 什么时候读 | 读哪份 |
|---|---|
| **做开源项目 / skill 介绍片** | `references/github-project-intro.md`（**8 页骨架 + 仓库地址页铁律 + 十七个坑**）· 样例 `assets/example-github-intro/` |
| **批量做一批项目介绍片** | 先跑 `python scripts/progress.py` 生成进度表（哪些做完 / 待做 / 缺仓库地址） |
| **第一次用** | `assets/example-relativity/`（一条真实成片的完整源码：8 页，看完就懂） |
| 画任何一页之前 | `references/page-api.md`（绘图 API 速查 + 三个高频坑） |
| 定分镜 / 写口播 | `references/storyboard-method.md`（五段式 + 禁忌） |
| 选风格 / 拿不准配色 | `references/style-packs.md`（五套风格 + 语法卡摘要） |
| `script.js` 字段不清 | `references/script-format.md` |
| 配音报错 / 想换 TTS | `references/tts-backends.md`（edge 已改走新域名，含回退说明） |
| 看不懂引擎报错 | `references/troubleshooting.md`（按症状索引） |

## 首次使用

如果 `scripts/` 报「引擎未就位」或依赖缺失，先跑 setup：

```bash
python scripts/setup.py                                    # 跨平台
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1  # Windows
```

**需要**：Node.js ≥ 22.19、Git、本机的 Chrome/Edge、Python 3.9+

首次约 2–4 分钟：从 GitHub 拉取引擎（约 16MB，sparse checkout 只取 `packages/engine`）+ `npm install` 依赖（约 130MB）。

**没装 Git**：手动下载 https://github.com/sitor-ai/frametell ，把 `packages/engine` 复制到 skill 根目录的 `engine/`，再跑一次 setup。

依赖清单与体积见 `README.md`；授权信息见 `vendor/ATTRIBUTION.md`。