# 故障排查

> 本文多数条目来自**真实制作一条 95 秒 8 页影片时踩到的坑**，按症状索引。

## ⚠️ 先看这个：过度打磨

做片子时最容易犯的错不是技术问题，是**在「lint 报的问题值不值得改」上反复纠结，把所有轮次修完才交付**。

**判断标准**：
- **必修**（blocker）：lint error、NaN、文字被色块盖住、图形完全没画出来 → 修完再渲染
- **可修可不修**（nice-to-have）：构图不够漂亮、留白不匀、某个元素位置微调 → **粗片先出去**

因为引擎有分段缓存，**改一页只重渲约 1 分钟**，所以「先交付 → 收反馈 → 再改」几乎零成本。

> 实测教训：那条 8 页片子，我在 lint 修完后又纠结了两轮构图才交付，用户等得不耐烦。
> 正确做法：lint error 修掉、明显 bug 修掉，粗片先出去。

## ★ 最常见的三类问题（先看这里）

### 1. lint 报 off-canvas / 压字幕带，但我坐标看着没问题

**十有八九是相机推镜（`P.push`）把元素放大了。** lint 检查的是**相机变换之后**的画面。

实测：p02 的「地球在动」放在 `x: 420` 完全合法，但该页有 `P.push(t2, 520, 520, 1.1)` —— 放大 1.1 倍后被推出左边界，报 `box -50,793–144,863`。

**修法**（按优先级）：
1. 元素往画面中间挪（x 400–1500，y 300–700）
2. 把 `P.push` 换成 `P.pan`（平移不改缩放，**最安全**）
3. 去掉这一页的相机动画

### 2. 文字整体位置不对（比预期偏左/偏右）

**不传 `w` 时 `x` 是左边缘，不是中心。** 见 `page-api.md` 的「文字居中」章节。

```js
P.text('站台', { x: 420, y: 640, w: 280, align: 'c', size: 46 });   // ✓ 中心在 420
P.text('站台', { x: 420, y: 640, size: 46 });                     // ✗ 从 420 向右铺开
```

### 3. lint 全绿，但画面很难看

**lint 只管硬错误**（出界/重叠/字号/密度），**不管构图**。必须看拼图：

```bash
python scripts/ftcheck.py <项目>        # 出 out/snap/pNN.jpg
```

然后**用 Read 工具逐页打开看**。构图问题只有眼睛能发现。

---

## 页面代码报错

### `R.rect is not a function`

`liveRough` 回调里的 `R` 只有 **4 个方法**：`box` / `circle` / `line` / `path`（见 `engine/runtime/live.js:82`）。

```js
P.liveRough((lt, R) => [R.box(x, y, w, h, { color: 'ink' })]);   // ✓
P.liveRough((lt, R) => [R.rect(x, y, w, h, {})]);                // ✗
```

### `R.box(...).options` 是 undefined

`R` 的方法**直接返回 options 对象**，不是包装对象。别解包。

### 控制台刷 `Expected number, "MNaN NaN CNaN NaN…"`，但不报错

**最常见的两个原因**（都不抛异常，lint 也可能全绿，只是图形画不出来）：

**① `P.check` / `P.cross` 的第三参数是「尺寸」，不是配置对象**

```js
P.cross(970, 716, { color: 'red', at: t })     // ✗ sz = [object Object] → r = NaN
P.cross(970, 716, 64, { color: 'red', at: t }) // ✓ 尺寸 64，配置在第四参
```

**② 变量遮蔽：liveRough 回调的第二个参数就叫 `R`（rough 对象）**

```js
const R = 1400;                                    // ← 会被回调参数覆盖
P.liveRough((lt, R) => (xL + R) / 2);              // ✗ NaN
P.liveRough((lt, rough) => (xL + xR) / 2);         // ✓
```

**定位方法**（逐页二分）：

```bash
node engine/tools/snap.mjs --only pNN 30.0 2>&1 | grep -c "NaN"
```

或者把该页砍到最小只留可疑的一行，再测。

### 页面完全没画出来（成片里那页空白/占位符）

```bash
node engine/tools/lint.mjs --only p03 --json
```

`kind: "runtime"` 的条目就是它。

### 画面每帧都在抖 / 两次渲染结果不同

页面代码里用了 `Math.random()` / `Date.now()` / CSS transition。**这是红线**——确定性是分段缓存、并行渲染、可复现的基础：

```js
const x = 300 + Math.random() * 100;   // ❌
const x = 300 + PV.rng(7) * 100;       // ✓
setTimeout(fn, 1000);                  // ❌
P.text('…', { at: P.c(1, 0.5) });      // ✓ 时间只用 P.c* 给的
```

自检：`ftcheck.py --determinism`

---

## setup 阶段

### 引擎未就位

skill 需要两样东西：**引擎**（约 16MB，setup 时从 GitHub 拉）+ **依赖**（约 130MB，npm 安装）。

正常跑 `scripts/setup.py` 即可。报错分几种情况：

**① 找不到 git**

引擎从 GitHub 拉取，没 git 走不通。装 Git：https://git-scm.com

或手动下载 https://github.com/sitor-ai/frametell ，把 `packages/engine` 整个目录复制到 skill 根目录的 `engine/`，再跑一次 `scripts/setup.py`（会跳过引擎，只装依赖）。

**② clone / sparse checkout 失败（网络问题）**

国内网络可试镜像：

```bash
git config --global url."https://ghproxy.com/https://github.com/".insteadOf "https://github.com/"
```

或直接手动下载（见上）。

**③ 依赖下载很慢**

依赖共约 130MB，其中 `ffmpeg-static` 占 80MB。换镜像：

```bash
npm config set registry https://registry.npmmirror.com
```

**④ 想跳过下载（你机器上已有 frametell）**

setup 会自动检测常见的 frametell 目录并复用其依赖。也可手动指定：

```bash
export FRAMETELL_ENGINE=/path/to/frametell/packages/engine
```

### 依赖检测误报「字体缺失」

`check_deps` 会依次找 `engine/node_modules`、`engine/../node_modules`、以及 roughjs 解析位置，能适配 pnpm 结构。仍误报就重跑 `python scripts/setup.py`。

### 找不到 Chrome / Edge

渲染靠本机浏览器（`playwright-core` 不自带）。装一个 Chrome/Edge，或 `export CHROME_PATH=...`。

---

## 配音阶段

### TTS 后端不可用

先跑探针看真实错误：

```bash
python scripts/ftvoice.py <项目> --backend apiz --probe
```

| 报错 | 原因 | 修法 |
|---|---|---|
| `voice id not exist` | 传了中文显示名 | 传 `voice_id`（`female-chengshu`）或预设名 `mature` |
| `找不到 apiz 命令` | 不在 PATH | 见 `tts-backends.md` |
| `429` / `余额不足` | 账户没钱 | `apiz account balance` |
| `WSServerHandshakeError 403` | edge-tts 被微软封 | 换 `--backend apiz` |
| `合成失败或产出为空` | 文本含控制字符 | 去掉换行符、控制符 |

### 配音和画面对不上

1. `voice.js` 里的 `t` 必须与 `script.js` 的 cue 文本**逐字相同**（引擎靠它匹配，`timing.js:50`）
2. 改了 `script.js` 但没重跑配音 → 画面用的是旧时长
3. 修法：`ftvoice.py <项目> --from N`

### 某句 0 字节

删掉对应的 `audio/pNN-cII-*.wav`，下次会重新合成。

---

## 渲染阶段

### 渲染很慢

正常。首次全量慢（87 秒片子约 2 分 45 秒）；**改单页时靠分段缓存约 1 分钟**。

快速预览：`ftrender.py <项目> --fps 24 --skip-subs`（快 40%）

### 渲染中途失败（`Error: node.exe 1`）

**直接重跑就行。** 实测遇到过：改完页面代码后重渲，视频和音轨都正常，只有字幕烧录那步崩了。重跑后 1 分钟出片——因为**视频分段和音轨已经进了缓存**。

```bash
python scripts/ftrender.py <项目>     # 直接重跑，不要清 out/
```

日志特征：报错在 `render.mjs:63`，但前面有 `✓ xx-无字幕.mp4  87.6s` —— 说明主要产物已完成。

### `✗ wrong length`（成片长度不对）

引擎自动校验 ±1s。检查是不是有页没配音频，或 `voice.js` 与 `script.js` 的 cue 文本不一致。

### 成片打不开

分段缓存里混进了坏文件。清掉 `out/chunks/` 后重渲（**其他文件不用删**）。

### 成片长度不对

引擎自动校验 ±1s，不符报 `✗ wrong length`。检查是不是有页没配音频。

### 画面底部全黑

Chrome 窗口比舞台矮。引擎已修，若仍出现：

```bash
export FRAMETELL_CHROME_ARGS=--window-size=1920,1080
```

### `schedule exceeds cue window`

一页要画的量超过这句口播的时长。改法：拆页 / 减元素 / 加长这句口播。

---

## Windows 特有

### `import('/d/path')` 报模块找不到

**实测踩过**：Python 调 node 时，`/d/path` 被解析成 `C:\d\path`。必须用 `file:///D:/path`。

### `node -e` 里的引号被 bash 吞掉

报 `Expected ',', got ':'`。**用双引号包裹 import 语句**——单引号会让 `file:///D:/` 内容丢失，并让 Windows 路径的冒号暴露在 eval 里。

### 软链接/junction 建不了

`ftnew.py` 用 junction（免管理员权限）。失败就重跑一次，会自动重试 `linkProject`。

### 中文变方块（豆腐块）

字体没加载，或用了字体没有的字形。检查 `node_modules/lxgw-wenkai-webfont/`。
避免生僻符号（`→` `≠` `∝`），拿不准就用中文词或 `P.icon` 画。

---

## 配音阶段

### TTS 后端不可用

先跑探针看真实错误：

```bash
python scripts/ftvoice.py <项目> --backend apiz --probe
```

**常见情况**：

| 报错 | 原因 | 修法 |
|---|---|---|
| `找不到 apiz 命令` | 不在 PATH | 见 `tts-backends.md` |
| `429` / `余额不足` | 账户没钱 | `apiz account balance` 看余额 |
| `WSServerHandshakeError 403` | edge-tts 被微软封 | 换 `--backend apiz` |
| `合成失败或产出为空` | 文本含特殊字符 | 去掉换行符、控制符 |
| `读不出音频时长` | 文件损坏 | 删掉对应 wav 重跑（缓存会重新合成） |

### 某句 0 字节

```bash
# 删掉这个文件，下次会重新合成
del audio/p01-c03-xxxx.wav
```

### 配音和画面对不上

1. 确认 `voice.js` 里的 `t` 和 `script.js` 的 cue 文本**逐字相同**（含标点）
2. 不一致 → 重跑 `ftvoice.py`（它按新文本重新算 hash 和时长）
3. `script.js` 改了但没重跑配音 → 画面用的是旧时长

---

## 质检阶段

### lint 报「文字出画布」「压在字幕带」

- 内容区硬边界：**x 140–1780 / y 180–880**
- y > 900 是字幕带，放内容会被判失败
- `P.title()` 自动落在左上（y≈70），不用管

### lint 报「文字太小」

渲染后 < 24px 就算失败。**正文写 32–56px**，别为了塞更多字而缩小。

### lint 报「文字重叠」

手工估位置很容易错。用 `PV.tw(text, size)` 量真实宽度再排：

```js
const w = PV.tw('这是一段文字', 48);
P.text('这是一段文字', { x: 400 - w / 2, y: 500, size: 48 });
```

### 拼图不出来（`snap` 失败）

通常是页面代码报错了。先看 `out/lint.json` 里的 `page` 字段，或单独跑：

```bash
node engine/tools/lint.mjs --only p02 --json
```

页面代码语法错时，引擎会让**那一页显示占位符但其余页正常渲染**，所以成片能出但那一页是空的。

---

## 渲染阶段

### 渲染很慢

正常。首次渲染 51 秒片子约 2 分钟（12 worker 并行）。改单页后靠分段缓存会快很多。

加速：
```bash
python scripts/ftrender.py <项目> --fps 24 --skip-subs   # 先看画面，跳过烧字幕
```

### `schedule exceeds cue window`

一页要画的量超过了这句口播的时长。改法：
- 拆成两页
- 减少这一页的元素
- 加长这句口播

### 成片打不开 / 长度不对

引擎会自动校验时长（±1s），不符会报 `✗ wrong length`。

先删掉坏的片段缓存重渲：
```bash
# 删整个 out/ 目录（分拍缓存损坏时也包括 chunks）
```
> ⚠️ **本机有 safe-delete 钩子**，`rm -rf` 类操作会被拦。逐个删文件，或直接换项目目录重渲。

### 画面底部全黑

Chrome 窗口尺寸比舞台矮导致。引擎已修（`capture-2` 标记），若仍出现：

```bash
# 用环境变量加参数
set FRAMETELL_CHROME_ARGS=--window-size=1920,1080
```

---

## Windows 特有

### `import('/d/path')` 报模块找不到

**实测踩过的坑**：Python 里调 node 时，`/d/path` 会被 Windows 解析成 `C:\d\path`。

skill 的脚本已统一用 `file:///D:/path`（见 `ftlib.py:file_url`）。如果你自己写脚本调 node，**必须**这样。

### 软链接/junction 建不了

`ftnew.py` 用 junction（免管理员权限）。若失败：

```bash
python scripts/ftnew.py <项目>    # 会重试 linkProject
```

### 中文变方块（豆腐块）

字体没加载。检查：

```bash
ls whiteboard-teacher-video/node_modules/lxgw-wenkai-webfont/
```

缺了重跑 `python scripts/setup.py`。另外**避免在页面代码里用生僻字和符号**（`→` `≠` `∝` 这类要看字体是否覆盖），拿不准就用中文词或 `P.icon` 画。

---

## 渲染确定性

引擎支持 `--determinism`：同一时刻渲染两次比对像素。页面代码里如果用了 `Math.random()` / `Date.now()`，这个检查会失败。

**这是有意的设计**——确定性是分段缓存、并行渲染、可复现的基础。红线：

```js
// ❌ 绝对不行
const x = 300 + Math.random() * 100;
setTimeout(fn, 1000);

// ✅ 正确
const x = 300 + PV.rng(7) * 100;
P.text('…', { at: P.c(1, 0.5) });   // 时间用 P.c 给的
```

---

## 目录变成几十万文件、删不掉

症状：`engine/` 莫名几百 MB 到 10GB、文件数几十万，`rm -rf` 跑十几分钟还没完，甚至越删越多、把别处的源码一起删掉。

原因只有一个：**目录环**。为了省 130MB，曾经把 `node_modules` 建成链接指向上游 monorepo，再让 `engine/node_modules` 链接回来。任何递归遍历（包括删除）都会顺着链接钻进上游源码树，来回打转。

**现在 setup 已经不建任何链接了**（依赖只有一份真实副本，在 `<skill>/node_modules`，引擎自己会向上找到它）。如果你接手的是旧版本，先确认并拆环：

```bash
# 1. 找出所有链接（Windows 上是 junction）
ls -la whiteboard-teacher-video/engine/        # node_modules -> ... 就是环

# 2. 只删链接本身，绝不能直接删目录
rm whiteboard-teacher-video/engine/node_modules          # 不要用 -r！
rm whiteboard-teacher-video/node_modules                 # 若它也是链接，同上

# 3. 确认没链接了再删
rm -rf whiteboard-teacher-video/engine
```

同样的道理适用于**项目目录**：`ftnew.py` 会让引擎在项目里建 `<项目>/engine` 这个 junction，所以删项目前也要先摘掉它，否则会把 skill 的 engine 连带删掉。另外**别把项目建在 skill 目录里面**——`ftnew.py` 已加了这条拦截。