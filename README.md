# whiteboard-teacher-video

**图文讲解视频 skill** —— 把讲解稿变成「手绘会动的画面」讲解视频。

图形由代码逐笔绘出、文字逐字写出、讲到哪画到哪。五套风格可选，本地 Chrome 渲染，**零生图 API 成本**，任何改动秒级重渲。

B站效果：https://www.bilibili.com/video/BV1yYJ46PE5R/?vd_source=86926e418c83af75f6850b5546388a79

安装方法，直接给链接给你的ai就可以。 本项目不需要依赖其他api，但是因为edge-tts语音最近被封了，所以建议安装 https://apiz.ai 的 apiz-cli 作为语音生成替代！

---

## 它和普通 AI 生视频工具的区别

| | AI 生视频工具 | 本 skill |
|---|---|---|
| 画面怎么来 | 模型生成像素 | **代码逐笔绘制**（rough.js） |
| 改一句话 | 整段重生成 | 只重渲受影响片段（**几秒**） |
| 画面质量 | 随机，有抖动 | 确定性，同一时刻渲染两次像素一致 |
| API 成本 | 按次付费 | **零**（只付 TTS 的钱） |
| 能嵌真实数据 | 难 | 任意数字/图表/代码/真实网页截图 |

**核心原理**：整片是「时间的纯函数」——`renderAt(t)` 渲染第 t 秒的画面，与之前播放过什么无关。由此才能分段缓存、并行渲染、任意跳转、确定性校验。

---

## 依赖到底要下载什么

**是的，要下载。** 但只有**两步**，都很轻。

### 第一步：取得引擎（约 16MB）

引擎**不在 skill 包里** —— 它有 16MB / 38 万个文件（主要是展开的 three.js），打进来会让分发变得很重。

setup 自动从 GitHub 拉取，用 **sparse checkout 只取引擎那一个目录**（不会下载上游几百 MB 的 electron 和桌面端）：

```bash
git clone --filter=blob:none --no-checkout --depth 1 https://github.com/sitor-ai/frametell
git -C frametell sparse-checkout init --cone
git -C frametell sparse-checkout set packages/engine
git -C frametell checkout
```

没装 git 也可以：手动下载仓库，把 `packages/engine` 整个目录复制到 skill 根目录下的 `engine/`。

### 第二步：第三方依赖（约 130MB）

`npm install` 自动获取，共 10 个包：

| 包 | 体积 | 作用 | 必须？ |
|---|---|---|---|
| `ffmpeg-static` | 80 MB | 音视频编码（自带 ffmpeg 二进制） | ✅ |
| `lxgw-wenkai-webfont` | 30 MB | **中文字体**（缺了中文变豆腐块） | ✅ |
| `playwright-core` | 13 MB | 驱动本机 Chrome/Edge 截图 | ✅ |
| `katex` | 4.4 MB | 公式排版（`P.tex`） | 可选 |
| `@iconify-json/logos` + `simple-icons` | ~4 MB | 品牌 logo（`P.logo`） | 可选 |
| `roughjs` | 275 KB | **手绘线条引擎** | ✅ |
| `@fontsource/*`（3 个字体） | 少量 | 英文手写体 / 圆体 / 等宽体 | 可选 |

**两点说明**：
- `playwright-core` **不含浏览器**，它只驱动你**本机已装**的 Chrome/Edge —— 不会额外下载几百 MB 的 Chromium
- 依赖**一律真实安装**在 `<skill>/node_modules`，不做任何复用链接。复用必须建 junction，而那会形成目录环（详见 `references/troubleshooting.md`）——130MB 换来的代价是几十万文件和删不掉的目录，不值得

### 对照：上游 frametell 原版要 1.3GB

| | 上游 monorepo | 本 skill |
|---|---|---|
| 依赖包数 | 590 个 | **10 个** |
| 安装体积 | 1.3 GB | **约 130 MB** |
| 安装耗时 | **24 分钟** | 1–3 分钟 |
| 多余内容 | electron、React 面板、模型层、桌面端 | 全砍掉 |

省掉 90% 体积和 90% 时间，因为 skill 不需要桌面 App、图形面板、模型接入 —— **干活的就是当前这个 agent**。

### 许可提醒

引擎是 **AGPL-3.0-only**（Sitor Team）。它作为独立进程被调用，**用本 skill 产出的视频不构成衍生作品**；但**不要把引擎源码复制进你自己的闭源项目**。详见 `vendor/ATTRIBUTION.md`。

---


## 快速开始

### 0. 克隆

```bash
git clone https://github.com/liangdabiao/whiteboard-teacher-video.git
cd whiteboard-teacher-video
```

### 1. 安装

**前置要求**：

| 需要 | 说明 |
|---|---|
| **Node.js ≥ 22.19** | 渲染引擎依赖 |
| **Git** | setup 用它从 GitHub 拉取引擎（无 git 可手动下载，见下） |
| **Chrome 或 Edge** | 渲染时驱动它截图（**不会**替你下载 Chromium） |
| Python 3.9+ | 跑 skill 的脚本 |

```bash
python scripts/setup.py                                     # 跨平台（macOS / Linux / Windows）
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1   # Windows PowerShell
```

首次约 2–4 分钟：拉取引擎（约 16MB）+ 安装依赖（约 130MB）。**装一次即可**，之后所有渲染都复用。

setup 会打印每个环境项的检查结果，标 ✗ 的项会说明怎么修。

**没装 Git？** 手动下载 https://github.com/sitor-ai/frametell ，把 `packages/engine` 整个目录复制到 skill 根目录下的 `engine/`，再跑一次 `scripts/setup.py`（它会跳过引擎那步，只装依赖）。

### 2. 五步做一支视频

```bash
# ① 建项目
python scripts/ftnew.py D:/films/relativity --title "相对论入门" --style whiteboard

# ② 写口播 → 编辑 D:/films/relativity/script.js（每页 2-3 句）
#    画画面 → 编辑 D:/films/relativity/pages/p01.js … pNN.js

# ③ 配音（逐句合成，自动缓存）
python scripts/ftvoice.py D:/films/relativity

# ④ 质检（lint + 每页拼图）—— 修到「没明显错误」即可，别追求完美
python scripts/ftcheck.py D:/films/relativity
#    ★ 然后用 Read 工具打开 out/snap/pNN.jpg 逐页看

# ⑤ 先出一个快版粗片给你看
python scripts/ftrender.py D:/films/relativity --fps 24 --skip-subs
```

产物在 `D:/films/relativity/out/`：成片 mp4（有/无字幕两版）+ `字幕.srt` + 每页拼图。

### 3. 看一个真实成品

《总统的证明：一块梯形证出勾股定理》—— **103.5 秒 / 8 页 / 黑板粉笔风**，讲加尔菲尔德 1876 年的那个证明。

https://www.bilibili.com/video/BV1yYJ46PE5R/?vd_source=86926e418c83af75f6850b5546388a79

它的价值在于示范了**一条贯穿全片的意象**（那块梯形）怎么用：

| 页 | 手法 |
|---|---|
| p03 | 纸堆打叉收成一块梯形 —— **主角在这里登场** |
| p04 | 梯形放大，标出三个直角标记与 a / b / c |
| p05 p06 p07 | **复用同一套归一化坐标**，只换高亮的边和填色，观众一眼认出是同一块 |
| p08 | 划掉 ab，绿字 a²+b²=c² 落在梯形正中收束 |

对应的分镜在 `assets/storyboard-总统的证明.json`。

### 4. 节奏建议：先出片，再打磨

**这是用好这个 skill 最重要的一条。**

用户要的是视频，不是完美的视频。建议这样推进：

| 阶段 | 做什么 | 耗时 |
|---|---|---|
| **粗片** | lint 无 error + 看一眼拼图没明显 bug → `--fps 24 --skip-subs` 渲染 → **交付** | 约 15 分钟 |
| **正式版** | 看用户反馈 + 自己再修一轮 → 正常渲染 → 交付 | 改单页约 1 分钟 |

因为引擎有**分段缓存**，改一页只重渲受影响的片段（一分钟），所以「先交付再迭代」几乎零成本——**攒着改完再交付反而让用户多等。**

### 5. 配音可选后端

```bash
python scripts/ftvoice.py <项目> --backend apiz   --voice mature  # 默认：成熟女声
python scripts/ftvoice.py <项目> --backend user   --user-audio D:/my-audios
python scripts/ftvoice.py <项目> --backend apiz --probe           # 只测可用性
```

> ⚠️ **edge-tts 已被微软 403 封锁**，不可用。详见 `references/tts-backends.md`。

---

## 五套风格

在 `script.js` 的 `META.style` 改一个词即可，页面代码不动。

| 风格 | 气质 | 适合 |
|---|---|---|
| `study`（默认） | 安静书卷、暖纸底 | 通用，拿不准就用它 |
| `whiteboard` | 白板马克笔、逐笔画出 | 数学推导、流程、逐步讲解 |
| `chalkboard` | 深绿板岩、粉笔颗粒 | 公式、课堂板书感 |
| `warm-story` | 暖色扁平插画 | 比喻叙事（理财、成长、心理） |
| `tech-dark` | 石墨深色、青色强调 | 软件、架构、终端、代码 |

**换的不只是配色，构图节奏和动画语法一起换** —— 每个风格包都带一份 `GRAMMAR.md`（做什么/不做什么）。

---

## 内置能力

- **29 个可复用组件**：图表（柱/线/雷达/仪表/矩阵）、流程图、终端、卡片、对话框、3D 点云
- **真实素材**：可嵌截图、视频片段、**真实网页截图窗口**（适合讲开源项目/产品）
- **公式**：KaTeX 排版
- **品牌 logo**：内置 simple-icons + iconify
- **竖屏**：加 `--portrait`（1080×1920）
- **字幕**：自动生成 SRT，可选烧录进画面
- **音画对齐**：关键数字用 `P.cw(i, '词')` 卡在「念到这个词的瞬间」

---

## 工作目录结构

一个视频 = 一个普通文件夹，纯文本代码 + 音频，没有任何二进制格式：

```
<项目>/
├── script.js       唯一事实来源：风格 + 口播 + 分页
├── voice.js        配音真实时间戳（ftvoice.py 自动生成）
├── audio/          每句一个音频切片
├── pages/pNN.js    每页画面（独立文件，可单独重渲）
├── storyboard.json 分镜
├── out/            成片、字幕、拼图、质检报告
└── engine →        引擎链接（junction，引擎自己建的）
```

> ⚠ **删项目目录前，先摘掉这个 `engine` 链接**（`rm <项目>/engine`，不要加 `-r`）。
> 带 `-r` 的递归删除会顺链接钻进 skill 的引擎里把它删掉。

---

## 脚本一览

| 脚本 | 作用 |
|---|---|
| `scripts/ftnew.py` | 建项目（铺骨架 + 建链接 + 写模板） |
| `scripts/ftvoice.py` | 配音 → audio/ + voice.js + 字幕.srt（多后端 + 缓存） |
| `scripts/ftcheck.py` | 质检（lint + 每页拼图 + 结构化报告） |
| `scripts/ftrender.py` | 渲染 + 成片校验 |
| `scripts/ftlib.py` | 公共库（路径、Windows 适配、音频探测） |

常用参数：

```bash
ftcheck.py  <项目> --only p03         # 只查一页
ftcheck.py  <项目> --no-sheets        # 只跑 lint 不出图
ftcheck.py  <项目> --determinism      # 加确定性检查
ftrender.py <项目> --fps 24 --skip-subs   # 快速预览
ftrender.py <项目> --portrait         # 竖屏
ftvoice.py  <项目> --from 5           # 从第 5 条重配（前缀不动）
```

---

## 常用环境变量

多数情况**不需要设任何环境变量**。这些是特殊情况下的出口：

| 变量 | 用途 |
|---|---|
| `FRAMETELL_ENGINE` | 引擎装在别处时指定它（如你想共用一份引擎） |
| `CHROME_PATH` | 指定浏览器可执行文件（默认自动探测系统 Chrome/Edge） |
| `FFMPEG_PATH` | 指定 ffmpeg（默认用 `ffmpeg-static` 内置的） |

---

## 性能参考（本机实测）

做一条 8 页 / 87 秒的片子（示例源码见 `assets/example-relativity/`）：

| 阶段 | 耗时 |
|---|---|
| 首次安装（引擎 + 依赖） | 约 2–4 分钟（16MB + 130MB） |
| 配音 26 句 | 约 1.5 分钟 |
| 质检（lint + 8 页拼图） | 约 1 分钟 |
| 渲染（首次，12 worker 并行） | 约 2 分 45 秒 |
| 渲染（改单页后，缓存命中） | **约 1 分钟** |
| 渲染（`--fps 24 --skip-subs` 快版） | 约 1 分 40 秒 |

**从建项目到第一条成片约 15 分钟**，其中大头是写页面代码的人力。
迭代单页一分钟——所以**「先交付粗片再改」几乎没有成本**。

> 示例：相对论那条片子（87.6 秒 / 8 页 / 1920×1080）的**源码**在 `assets/example-relativity/`，
> 分镜在 `assets/storyboard-相对论.json`——可以照着做自己的第一支片子。

---

## 许可与归属

**本 skill 分发时不含引擎源码** —— 引擎在用户 `setup` 时从上游 GitHub 获取（与 `whiteboard-explainer` 的 vendor 策略一致）。

- **引擎**：Frametell · Sitor Team · **AGPL-3.0-only** · https://github.com/sitor-ai/frametell
- **本 skill 自有部分**：`SKILL.md`、`scripts/`、`references/`、`setup.*`、`assets/` 均为原创
- **npm 依赖**：10 个包，各自宽松许可（详见 `vendor/ATTRIBUTION.md`）
- **字体**：霞鹜文楷 LXGW WenKai · SIL OFL-1.1（允许商用与再分发）

**AGPL 影响**：
- 引擎作为**独立进程**被调用，用本 skill 产出的视频**不构成衍生作品**
- ⚠️ **不要把引擎源码复制进你自己的闭源项目** —— 那会让你的项目整体变成 AGPL
- 需要非 AGPL 方案请另寻渲染引擎，或联系 Sitor Team 取得商业授权

完整归属与授权详见 `vendor/ATTRIBUTION.md`。

---

## 文档

| 读什么 | 打开 |
|---|---|
| **第一次用（强烈建议）** | `assets/example-relativity/` —— 一条真实成片的完整源码（8 页，含可复用写法） |
| 画页面前必读 | `references/page-api.md`（绘图 API + 三个高频坑 + 自检清单） |
| 定分镜、写口播 | `references/storyboard-method.md`（五段式 + 分镜 lint + 禁忌） |
| 选风格、配色 | `references/style-packs.md` |
| `script.js` 字段 | `references/script-format.md` |
| 配音报错、换 TTS | `references/tts-backends.md` |
| 报错查这里 | `references/troubleshooting.md`（按症状索引） |

---

## ★ 两件最重要的事

**一、lint 全绿 ≠ 画面是对的**

`lint` 只管机器能判的硬错误（出界/重叠/字号/密度），这些它**一律不管**：

- 构图好不好、元素挤不挤
- 文字有没有被色块盖住
- 图形符不符合本意（画出来像不像地球）
- NaN 导致的图形静默消失

所以 `ftcheck.py` 出拼图后，**必须用 Read 工具打开 `out/snap/pNN.jpg` 看一眼**。

> 实测：p07 那一页 lint 报 **0 错误**，但看拼图才发现「7 微秒」的「微秒」被荧光笔完全盖住，只剩一个红色的「7」——观众根本读不出单位。

**二、先出片，再打磨**

用户要的是视频，不是完美的视频。粗片也是片。

因为引擎有分段缓存，**改一页只重渲受影响片段（约 1 分钟）**，所以「先交付粗片 → 收反馈 → 再迭代」几乎没有成本；而**攒着改完再交付，只会让用户干等**。

---

## 三个高频坑（新手必看）

都来自实测制作一条 8 页影片的过程，**都不会报错，但会让画面不对**：

```js
// ① 文字居中：不给 w 时 x 是左边缘，不是中心
P.text('站台', { x: 420, y: 640, w: 280, align: 'c', size: 46 });   // ✓ 中心在 420
P.text('站台', { x: 420, y: 640, size: 46 });                     // ✗ 从 420 向右铺开

// ② check/cross 的第三参数是「尺寸」，不是配置对象
P.cross(970, 716, 64, { color: 'red', at: t });   // ✓
P.cross(970, 716, { color: 'red', at: t });      // ✗ sz = [object Object] → NaN

// ③ liveRough 的回调参数别叫 R；且 R 只有 box/circle/line/path
const R = 1400;                                    // ← 会被回调参数覆盖
P.liveRough((lt, R) => (xL + R) / 2);              // ✗ NaN
P.liveRough((lt, rough) => [rough.box(x, y, w, h, { color: 'ink' })]);  // ✓
```

另外两条不算坑但会翻车：

- **lint 报 off-canvas / 压字幕带，而坐标看着没问题** → 是相机 `P.push` 放大造成的，换成 `P.pan` 即可
- **`P.mark()` 荧光笔会盖住文字** → 荧光笔高度给到字号的 0.4 倍、放在基线下方。实测 p07 的「微秒」被完全盖住，lint 却全绿

---

## ★ lint 全绿 ≠ 画面是对的

`lint` 只管机器能判的硬错误（出界/重叠/字号/密度），**下面这些它一律不管**：

- 构图好不好、元素挤不挤
- 文字有没有被色块盖住
- 图形符不符合本意（画出来像不像地球）
- NaN 导致的图形静默消失

所以 `ftcheck.py` 出拼图后，**必须用 Read 工具逐页打开 `out/snap/pNN.jpg` 看一眼**。这是整个流程里最不能省的一步。

---

## 已知限制

- 不做写实照片/三维实拍风格（那是生图工具的领域）
- 不自动配乐（`page.sfx` 能做，但要自己准备音频文件）
- 逐句合成配音 → 整页语调略不连贯（要连贯需用火山/ElevenLabs 的字级时间戳方案）
- 建议 ≤ 12 页（每页都要写代码）

## 特别致谢

https://linux.do 社区支持