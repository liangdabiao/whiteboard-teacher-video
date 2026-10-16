# 示例：相对论入门（95 秒 · 8 页 · whiteboard）

这是一条**真实做出来的成片**的完整源码，不是伪代码。动手前先读它。

> 完整成片没放进 skill 包（8.4MB 太大）。想看效果就按下面的「怎么复现」跑一遍，约 15 分钟。

## 文件

```
example-relativity/
├── storyboard.json   分镜（先写这个，拿去给用户确认）
├── script.js         口播 + 分页（配音的输入）
└── pages/p01..p08.js 每页画面
```

## 这个例子演示了什么

| 页 | 演示的技术点 |
|---|---|
| p01 | `P.liveRough` 画行驶的火车（随时间平移，种子固定不抖）；剪影人物不画脸 |
| p02 | `P.liveRough` 画公转的地球；双色箭头对比；`P.pan` 而非 `push` |
| p03 | 「地基」隐喻：两块砖 + 顶部楼身 + 箭头连接 |
| p04 | 两条 `liveRough` 联动（船前进 + 差距线跟随），表达「永远差一点点」 |
| p05 | 同心扩散波前（闪光 + 传播波），用 `rough.line` 而非圆弧 path |
| p06 | 两个时钟秒针速度对比（同一 liveRough 内两条线，不同角速度） |
| p07 | 卫星轨道 + 数字强调 + `P.mark` 荧光笔 + 双路线对比 |
| p08 | 收尾落在动作（火车二次加速驶离 + 光射出），**不落金句卡** |

## 可直接复用的写法

### 1. 移动的东西（火车、行星、卫星）

```js
P.liveRough((lt, rough) => {
  const k = clamp((lt - t0) / 3.0);        // 0→1 进度
  const x = 100 + k * 600;
  return [rough.box(x, 300, 200, 100, { color: 'ink', sw: 3 })];
});
```

### 2. 秒针/指针类对比

```js
P.liveRough((lt, rough) => {
  const fast = (lt - t1) * 3.0;    // 快的那个
  const slow = (lt - t1) * 1.1;    // 慢的（相对论效果）
  const a = fast % (Math.PI * 2), b = slow % (Math.PI * 2);
  return [
    rough.line(lx, cy, lx + Math.cos(a - Math.PI/2)*88, cy + Math.sin(a - Math.PI/2)*88, { color:'ink', sw:3.4 }),
    rough.line(rx, cy, rx + Math.cos(b - Math.PI/2)*88, cy + Math.sin(b - Math.PI/2)*88, { color:'red',  sw:3.4 }),
  ];
});
```

### 3. 文字居中的正确写法（p05 就是反面教材）

```js
// ✓ 每页都是这样写的
P.text('站台', { x: px, y: py + 20, w: 240, align: 'c', size: 40, color: 'muted', at: t1 + 0.5, cps: 10 });
```

### 4. 相机：这个例子**全部用 pan，不用 push**

因为 `push` 会放大元素，导致边缘文字溢出画布、底部文字压进字幕带（lint 会报）。

```js
P.cam([P.pan(t1, 900, 570), P.back(P.endT - 0.3)]);
```

## 这条片子的实际数据

- 8 页，26 条口播，87.6 秒成片（30fps）
- 配音：apiz / `female-chengshu`（成熟女声）/ speed 1.15
- 质检：lint 0 error、NaN 0、逐页拼图确认
- 渲染：首次约 2 分 45 秒，改单页后约 1 分钟

## 这条片子踩过的坑（值得注意）

制作过程中真实遇到并修掉的问题，**都不报错、lint 一度全绿**：

| 坑 | 表现 | 修法 |
|---|---|---|
| 文字没给 `w` | 「地球在动」整体偏到画布外 | 每处文字都 `w` + `align:'c'` |
| `P.cross` 传配置对象 | 叉画不出来，控制台刷 NaN | `P.cross(x, y, 64, { color })` |
| 相机 `push` | 边缘文字被放大推出画布，lint 报 off-canvas | 全部换成 `pan` |
| `mark()` 荧光笔 | 「微秒」被完全盖住 | 荧光笔高度给字号的 0.4 倍 |

看 `pages/pNN.js` 里的注释，能看到这些修正的痕迹。

## 怎么复现

```bash
python scripts/ftnew.py D:/films/my-film --title "..." --style whiteboard
# 复制这个例子的 script.js 和 pages/ 进去
python scripts/ftvoice.py D:/films/my-film
python scripts/ftcheck.py D:/films/my-film
python scripts/ftrender.py D:/films/my-film
```

改 `script.js` 的口播后**必须重跑配音**（`voice.js` 的 `t` 要与 cue 逐字一致）。