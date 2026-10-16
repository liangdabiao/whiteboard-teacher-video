# 绘图 API 速查（画页面前必读）

画布 **1920×1080**（竖屏 1080×1920）。内容区 **x 140–1780 / y 180–880**，y > 900 是字幕带不许放内容。

页面骨架：

```js
ENGINE.visual('p03', (P) => {
  const { clamp, ease } = PV;          // PV 是全局工具库
  const t0 = P.c(0), t2 = P.c(2);      // 第 0 句 / 第 2 句开始的时刻

  P.title('页面标题', { accent: 'blue' });
  P.text('手写文字', { x: 300, y: 400, size: 56, at: t0, cps: 12 });
  P.cam([P.push(P.endT - 1.2, 950, 460, 1.15), P.back(P.endT - 0.3)]);
});
```

## 时间（最重要）

| 写法 | 含义 |
|---|---|
| `P.c(i, dt=0)` | 第 i 句开始 + dt 秒 |
| `P.cw(i, '词', dt=0, nth=0)` | 第 i 句**念到某词** + dt 秒（关键数字用这个） |
| `P.ce(i, dt=0)` | 第 i 句结束 + dt |
| `P.endT` | 本页口播结束时刻 |
| `at` / `dur` | 任何图元的 `at`=开始、`dur`=画完耗时（形状 0.5–1.0s，文字用 `cps` 每秒字数） |

`P.cw` 有字级时间戳时精确到字；无配音时间戳时按字数比例估算（仍可用）。

## 文字

```js
P.text(str, { x, y, size, color, w, align:'c', font:'hand'|'latin'|'mono',
              weight, at, cps, mode, lh })
```
- `cps` 每秒写几个字（白板风 10–14，插画风 6–8）
- `mode:'fade'` 整块淡入 | `'words'` 快速逐词写
- 内联标记：`{r:红色文字}`（r/b/g/o/p/m/s/k 分别是红蓝绿橙紫灰墨蓝）、`**粗体**`、`` `等宽` ``、`\n`
- `P.title(str, { accent })` — 左上角标题 + 手绘波浪线
- `P.code(lines, {...})` — 代码卡，可 `.hl(row, at, { n, color })` 高亮行

### ★★★ 文字居中：必须显式给 `w` + `align:'c'`

**这是最容易犯、且最难自查的错。** 看引擎源码 `runtime/text.js:82-85`：

```js
const align = o.align || 'l';          // ← 不传 align 默认左对齐
const w = o.w ?? (align === 'l' ? null : 1200);
el.style.left = (align === 'c' ? o.x - w/2 : align === 'r' ? o.x - w : o.x) + 'px';
```

于是：

```js
// ❌ 错：以为 x 是中心，实际 x 是左边缘，文字向右延伸出一大截
P.text('站台', { x: 420, y: 640, size: 46 });      // 从 x=420 向右铺开

// ✅ 对：显式给 w 和 align，x 才是中心
P.text('站台', { x: 420, y: 640, w: 280, align: 'c', size: 46 });
```

**判断规则**：想让文字以某点为中心 → 必须 `w` + `align:'c'`；只想让它从某点开始排（左对齐）→ 省略 `w` 即可，此时 `x` 是左边缘。

想量实际文字宽度（决定 `w` 给多大、或做精确排版）：

```js
const w = PV.tw('这是一段文字', 48);   // 返回估计像素宽
P.text('这是一段文字', { x: 960 - w/2, y: 500, size: 48 });   // 手动居中（无 wrap）
```

### ★ 相机推镜会让边缘元素溢出

`lint` 检查的是**相机变换之后**的画面。所以：

- 有 `P.push()` / `P.slam()`（放大）时，画面边缘的文字会被放大推出画布 → 报 `off-canvas`
- 有放大时，画面底部的文字会被推到字幕带里 → 报 `subtitle band`

**对策**：
1. 重要文字**放在画面中部**（x 400–1500 / y 300–700），别贴边
2. 这一页有 `push` 就**别把底部文字放太低**（y < 720）
3. 或者干脆**用 `pan` 代替 `push`**（平移不改变缩放，最安全）

实测：两页分别因为 `push` 导致文字溢出，改成 `pan` 后 lint 立刻全绿。

## 形状

```js
P.box(x,y,w,h, { fill, color, r, sw, dur, texture:false })
P.rect(x,y,w,h, o)   P.circle(cx,cy,diameter, o)   P.ellipse(cx,cy,w,h, o)
P.line(x1,y1,x2,y2, o)   P.path(d, o)   P.curve([[x,y],...], o)
P.arrow(x1,y1,x2,y2, { bend, head, dashed, color, sw })
```
所有形状默认**一笔一笔描出来**（rough.js 手绘感）。`fill` 填色，`texture:false` 关掉斜线填充。

## 强调（不靠特效靠笔法）

```js
P.ring(cx,cy,w,h, o)      // 圈起来
P.underline(x,y,w, o)     // 下划线
P.mark(x,y,w,h, o)        // 荧光笔（用 yellow）
P.check(x, y, size, o)    // 勾    ← 第三参数是尺寸
P.cross(x, y, size, o)    // 叉    ← 第三参数是尺寸
```

**★★ `check` / `cross` 的第三参数是「尺寸」，不是配置对象。**

实测踩过：写 `P.cross(x, y, { color: 'red', at: t })` 会把整个配置对象当成 `sz`，
于是 `sz / 2 = NaN`，控制台刷 `Expected number, "MNaN NaN…"`，
**但页面照样渲染、lint 也全绿** —— 叉就是画不出来，非常难查。

```js
P.cross(970, 716, { color: 'red', at: t })     // ✗ sz = [object Object] → NaN
P.cross(970, 716, 64, { color: 'red', at: t }) // ✓ 尺寸 64，配置在第四参
```

`P.markSpan(t, i0, i1)` / `ringSpan` / `underSpan` — 作用于**已写出的文字**的第 i0–i1 个字。

## 动态图形

```js
P.liveRough((lt, R) => [R.box(...), R.circle(...), R.line(...)])
```
每帧重画的草图，种子固定所以**不会抖**。适合：生长的柱、变粗的线、行驶的火车、旋转的齿轮。
`k = PV.K(lt, at, dur, ease)` 拿 0→1 的缓动进度，`clamp(lt - at)` 拿 0→1 线性进度。

### ★ R 只有 4 个方法，且直接返回 options

**实测踩过**：`R.rect(...)` 不存在——`rect` 是 `P` 上的方法，`R` 上没有。

```js
// ✅ R 上只有这四个（见 engine/runtime/live.js:82）
R.box(x, y, w, h, o)          // 圆角矩形
R.circle(cx, cy, d, o)        // d 是直径
R.line(x1, y1, x2, y2, o)
R.path(d, o)                  // SVG path 字符串

// ❌ 不存在：R.rect / R.ellipse / R.arc
// ❌ 不是对象：R.box(...).options 是 undefined，它本身就返回 options
const it = { ...R.box(...).options }   // ✗ 错
const it = R.box(1, 2, 3, 4, { color: 'ink' })   // ✓ 对
```

### ★★★ 变量名不要叫 `R`（会遮蔽，报 NaN 不报错）

**这是最隐蔽的坑**：JS 的参数遮蔽。引擎给 liveRough 回调的第二个参数就是 `R`（rough 对象）：

```js
const L = 520, R = 1400;          // ← 你声明的 R 是坐标

P.liveRough((lt, R) => {          // ← 这个 R 现在是 rough 对象，不是 1400
  const M = (L + R) / 2;          // ← L + [object Object] = NaN
  return [R.box(M, 100, 50, 50)]; // ← 路径属性全是 NaN
});
```

**症状**：控制台刷 `<path> attribute d: Expected number, "MNaN NaN CNaN NaN…"`。
**更糟的是它不报错**——页面照样渲染，只是那些图形消失或不显示。

**修法**：回调参数换个名字，别用单字母 `R`：

```js
P.liveRough((lt, rough) => {
  const M = (L + xR) / 2;
  return [rough.box(M, 100, 50, 50)];
});
```

**检查手段**：渲染时看控制台有没有 `NaN`。`ftcheck.py` 会把它打到 stderr。

其它：
- `P.follow(lt => ({ text, x, y, opacity }), o)` — 内容随时间变（计数器、数值）
- `P.bars(items, (i,lt)=>v, { x, base, bw, gap })` — 实时柱状图（支持负值）
- `P.slider(x,y,w,min,max,lt=>v, o)`
- `P.tex('E=mc^2', o)` — KaTeX 公式
- `P.canvas(x,y,w,h,(ctx,lt)=>{})` — 每帧重画的 canvas（热力图、点阵）

## 场景与相机

```js
P.layer() → 子层 Builder，.move((lt)=>({x,y,s,rot,op}))   // 整体移动
P.tick((lt) => { ... })                                  // 分节切换场景
P.cam([{ at, x, y, s, dur, ease }])                       // 相机关键帧
P.push(at, x, y, s=1.25)   // 0.28s 快速推近
P.pan(at, x, y)            // 0.30s 平移
P.slam(at, x, y, s=1.2)    // 冲过头再回落
P.shake(at, amp=10)        // 短促震动，全片最多 2 次
P.back(at)                 // 拉回全景
```
节奏是「**保持 → 快速移动 → 保持**」，不要整页匀速推。

## 组件

```js
P.icon(name, cx, cy, size, { at, fill, color, rot })
```
`name` 可选：`person robot wheel file terminal gear magnifier bulb wrench eye clock hourglass scissors warn door flag sun stack bird plug puzzle brain shield rocket fuse spinner chat cpu stop books sparkle`

```js
P.bubble(x,y,w,str,{side})   P.chip(x,y,w,str,{color})   P.card(x,y,w,h,{title})
P.keycap(x,y,label,{press})  P.stamp(x,y,str)            P.live(x,y,lt=>str)
P.tokens(list, o)             // 一排 token 块
P.logo(name, cx, cy, size)    // 真实品牌 logo（需先跑 logos.mjs）
```

## 真实素材

```js
P.img(src, x, y, w, h, { fit, at })          // 截图/插图
P.clip(name, x, y, w, h, o)                  // 帧序列视频片段
P.browser(x, y, w, h, { url, crop, pan })    // 真实网页截图窗口
```

## 颜色

**只写语义名，不许硬编码 hex。**

```
ink soft muted faint     ← 墨色由深到浅
blue orange red green purple yellow
blueF orangeF redF …     ← F = 该色向纸色的浅填充
paper
```
写了风格包里没有的颜色名会被质检发现（不会静默变黑）。详见 `style-packs.md`。

## PV 工具

```js
PV.K(lt, at, dur, ease)     // 0→1 缓动进度
PV.keys([[t,v],…], lt, e)  // 关键帧插值
PV.mix('blue','red', k)    // 两色混合
PV.rng(seed)               // 确定性随机（唯一允许的随机源）
PV.tw(str, size)           // 量文字宽度（避免猜位置）
PV.softmax(z, T)           // softmax
PV.mmss(sec)               // 185 → '3:05'
```

### ★ `mark()` 会盖住文字（必须画细、画在字下方）

**实测踩过**：`P.mark(1040, 420, 420, 110, { at: t2 })` 配 `P.text('7 微秒', { y: 430, size: 88 })`
—— 结果「微秒」两个字**完全看不见**，只剩红色的「7」。而且 **lint 全绿**。

原因：`mark` 是荧光笔色块，绘制顺序在文字之后就直接覆盖。高度给太大（110px 盖住 88px 的字）必然遮挡。

```js
// ✗ 荧光笔比字还高，直接盖住
P.text('7 微秒', { x: 1260, y: 430, size: 88, at: t2 });
P.mark(1040, 420, 420, 110, { at: t2 });

// ✓ 荧光笔只垫在文字下方一小条
P.text('7 微秒', { x: 1260, y: 380, size: 80, at: t2 });
P.mark(1070, 452, 380, 40, { at: t2 });     // 高 40，位置在字的基线以下
```

**经验值**：荧光笔高度 = 字号的 0.4–0.5 倍，`y` = 文字 `y` + 字号×0.8 左右。

---

## 常见错误

| 症状 | 原因 | 修法 |
|---|---|---|
| **文字位置整体偏移** | 没给 `w`，`align` 默认 `'l'`，`x` 是**左边缘**不是中心 | 居中必须 `w` + `align:'c'`（见上） |
| **控制台刷 `Expected number "MNaN…"`** | ① 变量遮蔽：liveRough 回调参数叫 `R` ② `check`/`cross` 把配置对象当尺寸传 | 见上面两条 |
| **`R.rect is not a function`** | `R` 只有 box/circle/line/path | 换 `R.box` |
| **`R.box(...).options` undefined** | R 直接返回 options，不是对象 | 直接用返回值 |
| **画面每帧都在抖** | 用了 `Math.random()` | 改 `PV.rng(seed)` |
| **渲染两次结果不同** | 同上，或用了 `Date.now()` | 全部去掉，只用 `P.c*()` 给的时间 |
| **lint 报 off-canvas 但我坐标没问题** | 相机 `push` 放大后元素溢出 | 元素往画面中间放，或用 `pan` 代替 `push` |
| **lint 报压字幕带但我没放那** | 相机推镜把底部文字放大了 | 同上；或文字 y < 720 |
| **某元素最后才出现** | 它的 `at` 晚于本页 `endT` | 核对 `P.c(i)` 的 i 是否超范围 |
| **文字变成方块** | 该字体缺这个字形 | 换引擎字体支持的字；符号用 `P.icon` 画 |
| **颜色没生效** | 硬编码了 hex | 改语义名 |
| **lint 报「文字太小」** | size < 24px | 正文 ≥ 32px |
| **lint 报「sparse page」** | 图形只占内容区不到一半 | 元素铺开一些，或 `pull` 相机拉远 |
| **文字被色块盖住（lint 不报）** | `P.mark()` 荧光笔太高，或画在文字之前 | 见上「mark 会盖住文字」 |
| **元素挤在一起（lint 不报）** | 手工估位置 | 分区用线隔开，各区留 40px+ |
| **文字互相重叠** | 手工估的位置 | 用 `PV.tw()` 量宽度后再排 |

## 交付前自检清单

**★ 最重要的一条：lint 全绿 ≠ 画面是对的。** lint 只管机器能判的硬错误（出界/重叠/字号/密度），
下面这些它一律不管，必须看拼图：

- [ ] **拼图逐页看过**（`ftcheck.py` 出 `out/snap/pNN.jpg`，用 Read 打开）——构图差、元素挤、
      **文字被色块盖住**、图形不像本意，这些只有眼睛能发现
- [ ] 每一页都 lint 过，`error` 为 0
- [ ] `ftcheck.py` 没有报 NaN（NaN 会让图形静默消失，但 lint 可能全绿）
- [ ] 每页元素铺得开（lint 无 `sparse` 警告）
- [ ] 重要文字在画面中部，没贴边；没被 `mark`/`box` 等色块盖住
- [ ] 有 `push` 的页面，底部没放低
- [ ] 首屏前 3 秒有东西在动
- [ ] 结尾落在**动作**上，不是居中金句卡
- [ ] 全片无 `Math.random()` / `Date.now()` / CSS transition

### 一条真实教训

p07 那一页 lint 报了 0 错误、质检脚本显示"全绿"，但看拼图发现：
**「7 微秒」的"微秒"两个字被荧光笔完全盖住，只剩下红色的「7」**——
观众看到的是"每天 7"，完全读不出是微秒。

`lint` 查不出元素被覆盖、图形不符合本意这类问题。**所以第 1 条不能跳。**