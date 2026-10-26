# GitHub 项目介绍视频：标准流程与骨架

> 用户说「给这个 md / 这个仓库做个介绍视频」「skill 介绍片」「项目宣传片」时，**照这份走**，
> 不要重新想结构。完整可运行样例在 `assets/example-github-intro/`（8 页，白板风）。

## 先理解这类片的特殊性

普通科普片的落点是「你懂了一个道理」；**项目介绍片的落点是「你知道这是哪个项目、去 GitHub 找它」**。

这两者的差别是致命的：

> **实测教训**：第一版做了 4 条项目介绍片，讲透了架构、机制、数据流，画面也干净，
> 但用户一句话打回来：「每一个文档不是有 `代码仓库：https://github.com/...`，**这个是核心**，
> 不然你在介绍什么，**核心就是介绍这些 github 项目**，但是你漏了介绍」。
>
> 观众看完不知道项目叫什么、在哪找 → 这条片子对「引流到仓库」毫无价值。

所以下面**第一节是铁律**，不是建议。

---

## ★ 铁律一：必须有「仓库地址页」，且是最后一页

每条项目介绍片，`pNN`（收束页之后）固定为地址页，`section: '仓库'`，标题「源码在这里」。

**页面四件套，缺一不可**：

| 元素 | 要求 |
|---|---|
| **仓库名大字** | 主角。等宽字体，字号按长度自适应：≤14 字符 → 78；≤22 → 76；>22 → 60 |
| **完整 URL** | `https://github.com/<owner>/<repo>`，等宽字体，通常 30–34px（长 URL 降字号别换行） |
| **owner 说明** | `<owner> 的仓库` |
| **怎么找** | 「搜仓库名，或直接照地址敲」+ 放大镜图标 `P.icon('magnifier', ...)` |

**口播固定 2 句**（照抄，只换仓库名）：

```js
{ id: 'p08', section: '仓库', title: '源码在这里', cues: [
  '这是它的 GitHub 仓库，liangdabiao 下的 <repo>。',
  { t: '搜仓库名，或者直接照地址敲，就能找到。', hold: 1.2 },
] },
```

**正文里至少报一次项目名**（如「ai-data-hub 把它们收进同一个底座」）。
通篇只说「它」「这个技能」，观众记不住。

## ★ 铁律二：仓库名/URL 必须从原文原样复制，不许推断

**仓库名 ≠ 文件名 slug**。实测这四个都不一样：

| md 文件名 | 真实仓库 |
|---|---|
| `ai-data-hub.md` | `AI_data_hub`（大写 + 下划线） |
| `whiteboard-explainer.md` | `whiteboard-explainer` |
| `geometry-math-proof-remotion.md` | `geometry-math-proof-remotion` |
| `xhs-business-validator.md` | `xhs-business-validator-skill`（多了 `-skill`） |

```bash
# 提取（一次拿准）
grep -m1 "代码仓库" <file>.md
```

**素材里没有 GitHub 地址怎么办**：
**先查项目里已有的清单文件** —— `github_repos_over_3_stars.md`（143 个仓库全表，含 star/语言/简介）、
`.workbuddy_meta.json`（slug → link）、`ALL-MERGED.md`。**这些是权威源，比联网搜快且准。**

> **实测教训**：有 7 个项目 md 里没写仓库地址，我只看了 `.workbuddy_meta.json` 和本地目录的
> `git remote`，就下结论「确实查不到」。用户一句话点醒：
> 「`github_repos_over_3_stars.md` 这个不就是全部啦，看这个就可以」。
> **「本地查不到」≠「不存在」**——排查类任务先把仓库里已有的清单文件翻一遍，再决定要不要联网。

在那份清单里按**关键词**比对（名字往往和 md 文件名不一样）：

| md 文件名 | 实际仓库 | 怎么确认的 |
|---|---|---|
| `glm-5.3-flash-vision-video-rag` | `glm-5.3-flash-vision-rag` | 简介写「三个 GLM 视觉技能总览」 |
| `pindou-pattern` | `perler-beads-skill` | 简介原文：「拼豆图纸生成器（**pindou**-perlerBeads-skill）」 |
| `talking-head-remotion` | `video-skills-toolkit/tree/main/skills/talking-head-remotion` | 大仓库里的同名子目录 |
| `mathigon-skill` | `textbooks` | 简介写「我制作了 **mathigon** textbooks skill」 |

**确实找不到对应项目**（本批 3 个，已确认不做）：`game-gameability`、`wechat-writer`、
`ian-xiaohei-illustrations` —— 清单里只有名字相近但**功能不同**的仓库
（boardgame-io 不是游戏性验证、wechat-article-remotion 是文章转视频不是写稿配图、
directing-xiaohei-videos 是动画不是配图）。**名字像不等于同一个项目，功能对不上就不做。**

确认映射写进 `scripts/progress.py` 的 `REPO_OVERRIDE`（地址 + 依据），
不做的写进 `EXCLUDE`，下次跑脚本自动生效。

---

## 标准 8 页骨架

> 7 页讲清项目 + 1 页仓库地址。总时长 70–85 秒，21 条 cue。
> 素材厚（≥5KB）就用满 7 页；素材薄（<1.5KB）压到 5 页，别硬撑。

| 页 | section | 讲什么 | 画面主角（必须是**具体物体**） |
|---|---|---|---|
| p01 | 开场 | 反直觉的事实 / 真痛点，**不是**「大家好今天介绍…」 | 左右对比：现状很糟 vs 有了它 |
| p02 | 问题 | 现在的做法为什么难受 | 一个具体的坏状态（断线、乱麻、打叉） |
| p03 | 解法 | 它是什么、怎么改变局面 | 核心意象登场（底座/秤/漏斗/管道） |
| p04 | 机制一 | 第一步做什么 | 一条流水线 / 一份输入的拆解 |
| p05 | 机制二 | 第二步做什么，**数据真的在动** | 元素沿路径移动（`liveRough`） |
| p06 | 机制三 | 关键产出（分数/图表/报告/接口） | 数字落在物体上，不是单独数字卡 |
| p07 | 收束 | 适合谁 + 边界（诚实说局限） | 岔路口 / 多个挂载点 / 落到动作上 |
| p08 | **仓库** | **这是哪个项目、去哪找** | **仓库名大字 + URL** |

**五段式映射**（见 `storyboard-method.md`）：Hook = p01，直觉 = p02，机制 = p03–p06，例子数字 = p06，收束 = p07 + p08。

### 从素材里该提取什么

按这个顺序扫一遍 md，**这五类信息都要用上**，缺哪类就去补：

1. **它是什么**（一句话定位）→ p03 的核心意象
2. **解决什么痛点** → p01 / p02
3. **具体机制 / 步骤 / 流程** → p04–p05（**必须是真步骤，不是形容词**）
4. **具体数字 / 档位 / 枚举** → p06（分数区间、时长、条数、模型名、字段名）
5. **适用人群 + 边界声明** → p07（边界要照实说，这是可信度）

> **素材厚度决定内容深度，不是页数。** 10KB 的 README 里有 20 个具体参数，
> 就不该压成 6 句口号。判断标准：**删掉这句，画面信息量会不会变？** 不变 → 这页是废话。

---

## 风格怎么选（项目介绍题材专用）

| 项目类型 | 风格 | 理由 |
|---|---|---|
| 软件架构、数据管道、CLI、MCP、Agent 框架 | `tech-dark` | 深色底像架构图，青色做通路 |
| 通用 skill、方法论、工作流 | `whiteboard` | 最百搭，马克笔感最像"讲解" |
| 数学 / 算法 / 公式推导类 | `chalkboard` | 板书天然适合边写边讲 |
| 商业 / 消费 / 心理 / 选品 | `warm-story` | 暖色扁平，需要一个贯穿比喻 |
| 拿不准 | `study` | 中性兜底，不出错 |

**warm-story 必须有贯穿比喻物体**（秤 / 存钱罐 / 岔路口 / 树）；
其余四种风格不需要，但最好也定一个反复出现的视觉锚点（管道、底座、流水线）。

---

## 可直接复用的页面模板

### ① 仓库地址页（**每条都要**，改 3 个变量即可）

```js
/* p08 仓库：这是哪个 GitHub 项目、地址在哪 —— 每条片子必须有这一页。 */
ENGINE.visual('p08', (P) => {
  const t0 = P.c(0), t1 = P.c(1);
  P.title('源码在这里', { accent: 'blue' });          // tech-dark 用 'blue'；chalkboard/warm-story 用 'yellow'/'orange'

  const REPO = 'AI_data_hub';                          // ← 从 md 原样复制
  const URL  = 'https://github.com/liangdabiao/AI_data_hub';

  // 窗口 / 卡片（tech-dark 用终端三点；whiteboard 用板书框；warm-story 用圆角卡片）
  P.box(240, 280, 1440, 400, { fill: 'paper', color: 'soft', r: 14, sw: 2.6, at: t0, dur: 0.6 });
  P.text('github.com', { x: 1620, y: 300, w: 300, align: 'r', size: 26, font: 'mono', color: 'muted', at: t0 + 0.5, mode: 'fade', dur: 0.3 });

  // 仓库名：主角，字号按长度自适应
  const sz = REPO.length <= 14 ? 78 : REPO.length <= 22 ? 76 : 60;
  P.text(REPO, { x: 960, y: 390, w: 1360, align: 'c', size: sz, font: 'mono', color: 'blue', weight: 700, at: t0 + 0.7, cps: 10 });
  P.text('liangdabiao 的仓库', { x: 960, y: 516, w: 1200, align: 'c', size: 32, color: 'soft', at: t0 + 1.2, mode: 'fade', dur: 0.4 });

  // 完整地址
  P.text(URL, { x: 960, y: 588, w: 1380, align: 'c', size: URL.length > 50 ? 30 : 34, font: 'mono', color: 'ink', at: t1, cps: 24 });

  // 怎么找
  P.text('搜仓库名，或直接照地址敲', { x: 1040, y: 754, w: 960, align: 'c', size: 40, color: 'ink', at: t1 + 1.2, cps: 10 });
  P.icon('magnifier', 460, 778, 78, { color: 'blue', at: t1 + 1.4, dur: 0.35 });
});
```

> **字号陷阱**：仓库名 88px + 下面一行 34px，垂直空间不够会报 overlap。
> 名字和「xx 的仓库」的 y 差要 ≥ 100px（上例 390 → 516，差 126）。

### ② 架构/流水线页（p04–p05 通用）

```js
const steps = [
  { x: 200,  cn: '摄取', en: 'Ingestion', ic: 'plug' },
  { x: 640,  cn: '加工', en: 'Transform', ic: 'gear' },
  { x: 1080, cn: '探索', en: 'Explore',   ic: 'magnifier' },
  { x: 1520, cn: '检索', en: 'Retrieve',  ic: 'eye' },
];
const BW = 320, BH = 300, BY = 320;
P.line(200, BY + BH + 96, 1840, BY + BH + 96, { color: 'faint', sw: 2.4, at: t0, dur: 1.0 });  // 轨道先画
steps.forEach((s, i) => {
  const t = t1 + i * 0.45;                                   // 依次落位，间隔 0.45s
  P.box(s.x, BY, BW, BH, { fill: 'paper', color: 'soft', r: 12, sw: 2.4, at: t, dur: 0.45 });
  P.icon(s.ic, s.x + BW / 2, BY + 104, 76, { at: t + 0.3, dur: 0.35 });
  P.text(s.cn, { x: s.x + BW / 2, y: BY + 156, w: BW, align: 'c', size: 46, color: 'ink', weight: 700, at: t + 0.45, cps: 8 });
  P.text(s.en, { x: s.x + BW / 2, y: BY + 220, w: BW, align: 'c', size: 30, font: 'mono', color: 'blue', at: t + 0.6, mode: 'fade', dur: 0.35 });
});
for (let i = 0; i < 3; i++)                                    // 箭头晚半拍
  P.arrow(steps[i].x + BW + 12, BY + BH / 2, steps[i + 1].x - 12, BY + BH / 2, { color: 'blue', sw: 2.4, head: 16, at: t1 + (i + 1) * 0.45 + 0.3, dur: 0.4 });
```

**这一页元素铺满内容区 → 不要写 `P.cam`**（pan/push 会把边缘推出画布）。

### ③ 数据真的在动（p05 的杀手镜头）

静态框图讲「流程」，观众记不住；**一个方块沿管道走过来**，观众就懂了。

```js
const go = t0 + 0.4, end = P.cw(2, '检索出来', 0.15);   // 说到关键词时正好走到终点
P.liveRough((lt, rough) => {
  if (lt < go) return null;
  const k = clamp((lt - go) / Math.max(0.5, end - go));
  const x = X0 + (X1 - X0) * k;
  const near = Math.exp(-Math.pow((x - 900) / 190, 2));   // 经过中间节点时形态变化
  const w = 108 - near * 58, h = 108 - near * 34;
  return [rough.box(x - w / 2, Y - h / 2, w, h, { r: 10, color: 'blue', fill: 'blueF', sw: 2.4 })];
});
```

> **回调参数别叫 `R`**（会遮蔽外部变量 → NaN，图形静默消失）。用 `rough`。

### ④ 数字落在物体上（p06）

不要做「居中大数字卡」。数字要挂在物体上：

- 分数 → 指针停在**刻度尺**的某一段（`P.follow` 跟着指针走）
- 占比 → 柱状图高度
- 延迟 → 箭头旁边的计时器
- 评分档位 → 四色刻度尺（`red` 风险 / `orange` 再验证 / `green` 有潜力 / `blue` 机会大）

---

## 效率流程（实测 22–25 分钟一条）

> **批量做之前先跑进度表**：`python scripts/progress.py`
> 它会扫素材目录 + 成片目录，生成 `PROGRESS.md`（已完成 / 待做 / 缺仓库地址 / 子路径仓库 / 各风格数量）。
> **状态是从事实算的**（`out/*-有字幕.mp4` 在不在），不要手改，做完一条重跑一次即可。

```
① 读 md（1 次 Read，别分片读）
② 写 script.js（8 页 × 3 句 = 21 条 cue）
③ ★ ftvoice.py 丢后台 ←── 关键：配音 1.5–2.5 分钟，期间并行写 8 页画面
④ 一次性写完 pages/p01–p08.js（多个 Write 并行提交）
⑤ ftcheck.py 全量 1 轮 → 只修 error
⑥ 有点位错误 → ftcheck.py --only pNN --no-sheets 定点复查（几秒）
⑦ ftrender.py --fps 24 → 交付
```

**四条省时纪律**：

1. **配音先起，别等**。`ftvoice.py` 后台跑，写完页面正好配完。
2. **定点复查用 `--only`**，别全量重跑 8 页。
3. **`--fps 24`**，比 30 快 20%，肉眼几乎无差。
4. **lint 0 error 就直接渲染**，不要去追求构图完美（warn 一律放过）。

**不要做的事**：
- ❌ 反复跑 3 轮以上 ftcheck「精益求精」（用户明确制止过两次）
- ❌ 批量渲染用 `for` 循环串多条（见坑 6）
- ❌ 攒着全部修完才交付（粗片也是片）

---

## 十七个坑（都实测踩过）

| # | 症状 | 原因 | 修法 |
|---|---|---|---|
| 1 | 整页白屏 + `empty-opening`/`empty-ending`/`sparse` 三个 error | `P.path(d)` 的 `d` 漏了开头 `M` → `Param not a number: L,H` | 模板字符串开头必带 `M`：`` P.path(`M${x} ${y} L...`) `` |
| 2 | `subtitle band (y>905)` 但文字明明在 880 | 相机 `push` 放大 1.05–1.12 倍，把底部文字顶进字幕带 | 有底部文字就别写 `P.cam`；必须推就把倍数压到 ≤1.05 且中心上移 |
| 3 | lint 全绿，但看图发现字被色块/图形压住 | **lint 只查文字↔文字重叠，不查图形↔文字** | 必看拼图；本模型读不了图时，靠**坐标自查**（算 clearance） |
| 4 | 同页两组文字 15%–87% 重叠 | 大标题和编号/标签的 y 挨太近 | 同一水平带只放一种文字；垂直间距 ≥ 字号 × 1.4 |
| 5 | 深度图风格里出现橙绿蓝三色小图标 | `P.icon('books')` 等图标自带多色 `fill` | 需要单色就自己 `P.path`/`P.ellipse` 画；`icon` 的 `color` 只管描边 |
| 6 | 批量渲染报 `SAFE_DELETE_BULK_CONFIRM_REQUIRED` | 一个 turn 内累计删除超阈值（50 文件） | **一条一个命令渲染**，不要 `for` 循环 |
| 7 | 重渲报 Security Center 拒绝写 `seg-xxx.part.mp4` | 上次中断留下 `.part.mp4` 残留 | 先 `rm -f out/chunks/*.part.mp4`，再单独重渲（别同 turn 批量删+渲） |
| 8 | `Read out/snap/pNN.jpg` 报「模型不支持读取图片」 | 当前模型无视觉能力 | 别把「看图」写进流程假设；靠 lint + 坐标自查，并**如实告诉用户未肉眼核验** |
| 9 | 元素最后才出现 / 提前出现 | `P.c(i)` 越界**不报错**，会回退到最后一个 cue 的起点 | 每页 3 句就只用 `P.c(0..2)`；要延迟用 `P.c(i, dt)` |
| 10 | 文字整体偏右一大截 | `P.text` 不给 `w` 时 `x` 是**左边缘**，`align` 默认 `'l'` | 居中必须给 `w` + `align:'c'` |
| 11 | 前台渲染命令跑一半就断、无产物 | 单条渲染也可能超过前台超时 | **渲染一律 `run_in_background`**，用任务通知收结果，不要前台硬等 |
| 12 | 三条配音串行跑，第 3 条被 safe-delete 拦 | 配音也会删临时音频，累计计入同一阈值 | **配音也一条一个命令**；被拦了单独补跑即可（已合成的会复用，很快） |
| 13 | 两条 `ftvoice.py` 同时跑，后一条直接崩 `SHFileOperationW 0x2` | **两个 ffmpeg 进程争抢同一临时文件/回收站操作** | **配音严格串行**，一条跑完再起下一条 |
| 14 | 一条在后台渲染时又起一条，新的那条跑到一半断、无产物 | 同上：ffmpeg 任务不能并发 | **渲染也串行 + 后台**；被中断的清 `out/chunks/*.part.mp4` 后单独重跑 |
| 15 | `ftcheck` 报「没有 script.js」，补上后又报 `ERR_FILE_NOT_FOUND index.html`、lint 输出非 JSON | **`ftnew.py` 与 `Write script.js` 被并行执行**：Write 先落地 → ftnew 判定「项目已存在」→ **跳过 `createProject`**（index.html / out / audio 全没建），随后 `rm` 又把 script.js 删了 | **先单独跑完 `ftnew.py`，再写 script.js 与 pages，绝不并行**。已毁的项目复制同风格项目的一份 `index.html`（4 行）即可救回 |
| 16 | lint 报 `small text (23px < 24px)`，但代码里写的是 `size: 24` | 引擎按 0.96 折算实际像素 | 想过 small-text 就让字号 **≥ 26**，别卡在 24 |
| 17 | **某页的后几句完全没配音**，渲染报 `these lines have no narration yet`；`ftvoice` 却显示「✓ 成功」 | **cue 文案里出现了 `]`**。`ftlib.parse_script` 用非贪婪正则 `cues:\s*\[(.*?)\]` 提取，遇到文案里的 `]` 就提前截断，该页后续 cue 全部丢失 | **cue 文案禁止出现 `]`**（也不要 `[`）。要念"时间码"就写「分秒时间码」，别写 `[MM:SS]`。**判断信号：ftvoice 报的 cue 数 < 预期数**（如 8 页应有 23 条却报 21 条）→ 立刻查该页文案 |

> **坑 6/7/11/12/13/14 的统一教训**：这套工具链的瓶颈不在渲染速度，在**并发与批量操作阈值**。
> **同一时刻只能跑一个 ffmpeg 相关任务**（配音、渲染都算）。"并行"只适用于**写代码**——
> 多个 `Write` 可以同时提交，但配音和渲染必须排队。
> **但 `ftnew.py` 属于"建工程"而不是"写代码"，它必须独占一步**（坑 15）。
> 所以省时的正确姿势是：**一个在跑音视频，另一个人在写页面代码**，而不是同时跑两条片子的音视频。

### 仓库名按长度选字号（实测表）

| 仓库名字符数 | 字号 | 排法 | 实测案例 |
|---|---|---|---|
| ≤ 10 | 92–104 | 单行，可以很大 | `geolook`（92） |
| 11–22 | 62–78 | 单行 | `Amazon-Skills-Liang`（70）· `claude-data-analysis`（76） |
| 23–30 | 60–64 | 单行，`w` 给到 1400 | `stem-illustration-skill`（64） |
| 31+ | 54–62 | **按连字符拆两行**，各自 58–62 | `Bright-Data-MCP-Claude-Skill` / `deep-research`；`Amazon-listing-alexa` / `optimizer`；`Claude-Code-Stock` / `Deep-Research-Agent` |

**★ 大字下方文字的间距公式**：`P.text` 行高是 `字号 × 1.45`。
所以「仓库名 y=372、字号 92」的底边在 `372 + 92×1.45 = 505`，
下面那行「xx 的仓库」**y 必须 ≥ 512**，否则就是 20%+ 的重叠警告。
> 实测踩过：104 号字放 y=400，底边 551，压住了 y=540 的说明文字。

**URL 字号**：≤40 字符 → 30–34 号；41–60 → 26–28 号；>60 → 24–26 号 + 底条承托。
实测 101 字符的 URL 用 24 号刚好不溢出。

---

## 交付前检查清单

**内容层（比画面重要）**
- [ ] 最后一页是**仓库地址页**，仓库名 + 完整 URL + owner + 怎么找，四件齐全
- [ ] 仓库名/URL 是从 md **原样复制**的（不是按 slug 拼的）
- [ ] 正文至少报过一次**项目名**
- [ ] 素材里的**具体数字/档位/枚举**进了片子（不是只有结论句）
- [ ] p07 说了**边界**（不能干什么），不是纯吹

**画面层**
- [ ] `ftcheck.py` 全量跑过 1 轮，error = 0
- [ ] 无 NaN（`ftcheck` 会打到 stderr）
- [ ] 底层铺满内容区的页没有写 `P.cam`
- [ ] 有相机 `push` 的页，底部没放低（y < 720）
- [ ] 首屏 3 秒内有东西在动
- [ ] 结尾落在**动作**上（箭头延伸 / 方块移动），不是居中金句卡

**产物层**
- [ ] `out/<name>-有字幕.mp4` 存在且大小合理（67 秒 ≈ 4–8MB）
- [ ] `out/字幕.srt` 存在
- [ ] 渲染日志有「音轨：有」

---

## 一批做完 100+ 个项目时：靠进度表，别靠脑子

单条片子 20 分钟能做，但 **138 条就是 46 小时**——这种规模必须靠表格管理，否则一定会：
漏掉某些项目、重复做同一个、忘了哪个缺仓库地址。

`scripts/progress.py` 是唯一事实来源，它从**事实**重新算状态：

| 数据 | 从哪来 |
|---|---|
| 项目清单 | `<素材目录>/*.md`，排除 `ALL-MERGED`/`README`/`MISSING-DOCS`/`_aefs_readme_backup` |
| 仓库地址 | md 里的「代码仓库：」行优先，缺失则用 `.workbuddy_meta.json` 的 `link` |
| 完成状态 | `<成片目录>/<项目>/out/*-有字幕.mp4` 是否存在 |
| 实际风格 | 已完成项读 `script.js` 的 `META.style`（比关键词猜准） |
| 建议风格 | 关键词推断（仅供排序参考，制作时按内容判断） |

```bash
python scripts/progress.py                       # 默认扫 E:/all-skill-t0/skill-intros → D:/films/PROGRESS.md
python scripts/progress.py --src ... --films ... --out ...
```

**它会主动暴露三类坑**，正好是批量时最容易翻车的地方：

1. **缺仓库地址** —— 这些项目地址页不能编，必须先去 `.workbuddy_meta.json`、
   同级项目目录的 `git remote`、或 GitHub 搜核实；仍找不到就把地址页改成「项目名 + 搜项目名」
2. **仓库是子路径**（`.../tree/main/SKILLS/skills/xxx`，本批有 23 个）——
   地址页要同时显示**父仓库 + 子路径**，只显示最后一段观众找不到
3. **素材偏薄**（<1.5KB，本批 60 个）—— 这类压到 5 页，别硬撑 8 页，否则全是废话

### 建议的批量节奏

- **序**：按各组内「素材厚度降序」推进。厚的先做，内容撑得起 8 页，不容易做成空壳。
- **批**：一批 3–5 条，出片后汇报；不要闷头做 20 条再给用户看。
- **同批同风格**：配音语速、画风、节奏更容易统一，返工少。
- **每批做完重跑 `progress.py`**，让表跟上，别积累偏差。

---

## ★★ 系列片：N 个 md 合成一条（省时最狠的一招）

**先分组，再动手。** 一批 md 里往往有大量「同一仓库的多个子技能」或「同一套模板的多个变体」，
给它们各做一条 8 页片，内容会高度重复，观众也记不住区别。

> **实测**：135 个 md 里有 **34 个**属于 8 个系列（edulab 7 个、amazon-sorftime 9 个、
> claudesdk 8 个……）。合并后产出单元从 118 降到 **92**，**一条片覆盖 7 个 md**。

### 怎么判断能不能合

| 情况 | 能合 | 说明 |
|---|---|---|
| 同一个仓库下的多个子目录 | ✅ | `edulab/skills/edu-*` 7 个 → 1 条 |
| 同一套模板、多个独立仓库 | ✅ | `claudesdk-*-chat` 7 个 → 1 条 |
| 只是主题相近、实现无关 | ❌ | 别硬凑，会讲成流水账 |

分组方法：按仓库地址（`github.com/<owner>/<repo>` 作为 key）聚类，
`.workbuddy_meta.json` + md 里的「代码仓库」行就够。

### 系列片的结构（和单片不同，重点在 p04–p06）

单片讲「一个项目怎么运作」，**系列片讲「这一族怎么分类、每个成员管哪块」**：

| 页 | 系列片该怎么改 |
|---|---|
| p01 开场 | 讲**整族的共同痛点**（不是某个项目的痛点） |
| p02 问题 | 现在的笨办法，为什么不行 |
| p03 解法 | **强调"这不是一个技能，是一个仓库/一套"**——破掉观众的预期 |
| **p04 机制一** | **归纳成 2–3 类呈现形态**（这是系列片的灵魂，七个记不住、三类记得住） |
| **p05 机制二** | **成员共有的结构**（统一的三栏/统一的接口/统一的调用方式） |
| **p06 机制三** | **分工矩阵**：一行一类、一格一个成员，观众对号入座 |
| p07 收束 | 整族适合谁 + 边界 |
| **p08 仓库** | **只给父仓库 + 「成员在 xxx 目录」**，不要列 7 个成员名 |

### ★ p08 的反直觉结论：系列片地址页**不要**列成员清单

第一版我在 p08 塞了 7 个子目录名，结果字号被压到 **20px**（lint 报 small-text），
地址页反而看不清。**成员分工在 p06 已经讲清了，p08 重复列是信息浪费。**

正确做法：
```
仓库名大字（92–104px）
完整 URL（父仓库）
一句话：「七个技能，都在 skills/ 目录下」
```

**多仓库系列（成员是 N 个独立仓库）——用「前缀」当入口**（2026-10-23 实测）：
`claudesdk` 那族有 8 个独立仓库，逐个列名必然把字号压到 20px。
改成给**公共前缀**：
```
claudesdk-          ← 84px 大字
八个仓库共用这个前缀
https://github.com/liangdabiao
[claudesdk-exa-chat] [claudesdk-seedance-chat] [claudesdk-amazon-chat]   ← 3 个例子
搜 claudesdk，八个全出来
```
观众记一个前缀，比记八个全名容易得多。

**超长仓库名**（≥25 字符，如 `llm-wiki-claude-agent-sdk-agentic-rag` 37 字符、
`GEO-Content-Optimizer-Skill` 27 字符）→ **按连字符拆两行，各 56–58 号**，
下面配 25–26 号的完整 URL 加底条承托。

### 在 `progress.py` 里登记

```python
SERIES = [
    {
        "slug": "series-edulab",                 # 成片目录 D:/films/series-edulab
        "title": "edulab · 数学与理科交互课件合集",
        "repo": "https://github.com/liangdabiao/edulab",
        "style": "chalkboard",
        "covers": ["edu-plane-geometry", "edu-solid-geometry", ...],
    },
]
```

登记后脚本会自动：
- 把这 N 个 md 从「单片待做」里剔除
- 系列片出片后，**N 个 md 同时标记为已覆盖**
- 进度表单独列出「🎬 系列片」小节

⚠️ **已被单独做过的 md 要从 `covers` 里去掉**，否则会重复计数
（`edu-analytic-geometry` 先单独出了片，就没算进 `series-edulab`）。

### 系列片命名

`series-<仓库名或族名>`，例如 `series-edulab`、`series-claudesdk`、`series-amazon-sorftime`。
一眼就能在 `D:/films/` 里认出哪些是系列片。

---

## 参考实现

`assets/example-github-intro/` —— 完整 8 页源码（白板风，介绍本 skill 自己）：

```
script.js          21 条 cue，8 页，gap 0.5
pages/p01.js       开场：翻页的 PPT vs 正在画的圆（对比）
pages/p02.js       真手绘：房子分三笔描出（笔法演示）
pages/p03.js       音画对齐：旁白时间轴 + 念到"月亮"才画月牙（P.cw）
pages/p04.js       两种模式：左右分屏（逐拍 vs 单画布生长）
pages/p05.js       本地 CPU：云端打叉 vs 本机 cpu（对比）
pages/p06.js       工具链：四段流水线 PIL/Agnes/edge-tts/ffmpeg
pages/p07.js       适合谁：三张场景卡 + 收尾箭头
pages/p08.js       仓库地址页 ← 所有项目介绍片都必须有这页
```

**怎么用**：`cp -r assets/example-github-intro D:/films/<新项目>`，
再 `ftnew.py` 建骨架（它会补上 `engine` 链接），然后改 `script.js` 的口播 + 各页内容。
**不要照抄它的配色和图形**——只抄结构和节奏，每个项目要有自己贴合内容的画法。

---

## 实战验证：这套骨架跑过哪些题材

2026-10-22 用这套 8 页骨架连做 3 条**不同形态**的片子，验证骨架是否通用：

| 项目 | 形态 | 风格 | 时长 | 质检 | 骨架适配点 |
|---|---|---|---|---|---|
| `brightdata-research` | MCP / 数据抓取工具 | tech-dark | 81s | 0 错 | p04 四把铲子 → 4 卡横排；p05 三轨并发抓取 |
| `claude-data-analysis` | 数据分析技能集 | study | 84s | 0 错 | p03 七模块 + 六阶段双层；p05 一句话路由（光束射向命中模块）|
| `flue-framework` | TypeScript Agent 框架 | tech-dark | 86s | 0 错 | p02 用代码卡对照错误/正确写法；p04 `P.code().hl()` 高亮 |

**结论：8 页骨架对「工具类 / 集合类 / 框架类」三种形态都成立**，只需替换 p04–p06 的载体：
- 工具类 → **能力卡**（四把铲子）
- 集合类 → **模块网格 + 主干流程**（七模块 + 六阶段）
- 框架类 → **代码卡 + 装配示意**（createAgent / defineTool）

**三条共用的固定件**（不要每次重新设计）：
1. p01 用**对比**（天平 / 散乱 vs 有序），不用「大家好今天介绍…」
2. p02 讲**具体的坏状态**（撞墙弹回 / 来回跳 / 报错）
3. p07 一定说**边界**（要 token、要守条款 / 入口型集合 / 两个坑）
4. p08 仓库地址页四件套

