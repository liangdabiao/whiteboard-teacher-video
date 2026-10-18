# 第三方归属（Third-party attribution）

本 skill 分发时**不含**任何引擎源码或第三方二进制；它们在用户首次 `scripts/setup.py` 时自动获取。

---

## Frametell 视频引擎

| 项 | 值 |
|---|---|
| 用途 | 本 skill 的渲染内核：页面运行时、风格包、组件库、质检工具、渲染管线 |
| 上游 | https://github.com/sitor-ai/frametell |
| 版权 | Sitor Team (https://sitor.ai) |
| 许可 | **AGPL-3.0-only** |
| 版本 | 0.7.2 |
| 获取方式 | setup 时 `git clone --filter=blob:none --no-checkout --depth 1` + sparse checkout，只拉 `packages/engine`（约 16MB） |

### 为什么引擎不进 skill 包

引擎有 **16MB / 38 万个文件**（主要是展开的 three.js）。打进 skill 包会让分发体积和克隆速度都很糟糕。

因此采用与 `whiteboard-explainer` 相同的策略：**只声明来源，安装时拉取**。

> 对比：`whiteboard-explainer` 的引擎 `whiteboard-animator` 已发布到 PyPI（`pip install whiteboard-animator==0.1.1`）。
> Frametell 的 engine 目前**未发布到 npm**（其 package.json 标记 `"private": true`），所以改为直接从 GitHub sparse checkout 获取。

### ⚠️ AGPL 影响（重要）

AGPL-3.0 是强 copyleft。**由于引擎是 AGPL，用本 skill 产出的视频不构成衍生作品**（引擎不在分发物中，且仅作为独立进程被调用），但：

1. **不要把引擎源码复制进你自己的闭源项目** —— 那会让你的项目整体变成 AGPL
2. **不要试图剥离或替换 Frametell 的署名**（除非你另写了独立实现）
3. 本 skill 自身的代码（`scripts/`、`references/`、`SKILL.md`、`setup.*`）为原创，与上游无关

若你需要一个**不依赖 AGPL**的方案：请改用其它渲染方案，或联系 Sitor Team 取得商业授权。

---

## 第三方 npm 包（由 `npm install` 自动获取）

以下由 `package.json` 声明，setup 时自动下载，**均不随 skill 分发**：

| 包 | 体积 | 用途 | 许可 |
|---|---|---|---|
| `ffmpeg-static` | 80MB | 音视频编码（内置 ffmpeg 二进制） | ffmpeg 本体为 LGPL/GPL，详见该包 |
| `lxgw-wenkai-webfont` | 30MB | 中文字体（霞鹜文楷） | **OFL-1.1** |
| `playwright-core` | 13MB | 驱动本机 Chrome/Edge | Apache-2.0 |
| `katex` | 4.4MB | 公式排版（`P.tex`） | MIT |
| `@iconify-json/logos` | ~2MB | 品牌 logo（`P.logo`） | 各商标归属其公司 |
| `simple-icons` | ~2MB | 品牌图标源 | CC0-1.0 |
| `roughjs` | 275KB | **手绘线条引擎** | MIT |
| `@fontsource/caveat` / `fredoka` / `jetbrains-mono` | 少量 | 英文手写体 / 圆体 / 等宽体 | OFL-1.1 / MIT |

### 关于 `playwright-core`

**它不包含浏览器**，只是驱动你本机已安装的 Chrome 或 Edge。所以不会额外下载几百 MB 的 Chromium。

### 关于 `ffmpeg-static`

包含 FFmpeg 可执行文件。FFmpeg 通常以 **LGPL**（若不带 `--enable-gpl`）或 **GPL** 构建。
若需在你的商业产品中分发，请自行确认该构建的许可证条款。

---

## 外部服务（不随 skill 分发）

- **TTS 配音**：默认用 `apiz`（用户自行安装 CLI 并提供账号）→ `edge`（免费，走 `api.msedgeservices.com`）→ 火山方舟 / ElevenLabs（需自备 key）
- **注意**：`edge` 的旧域名 `speech.platform.bing.com` 在部分地区 403；helper 已改走新域名，仍属微软服务，使用前请自行确认条款

---

## 本 skill 原创部分

以下为本项目原创，不来自任何上游：

- `SKILL.md`、`README.md`、`package.json`、`scripts/setup.py`、`scripts/setup.ps1`
- `scripts/ftlib.py`、`ftnew.py`、`ftvoice.py`、`ftcheck.py`、`ftrender.py`
- `references/*.md`（6 份技术文档）
- `assets/example-relativity/`（基于本 skill 实际产出的示例片源码）
- `assets/storyboard-相对论.json`

设计思路（纯函数时间轴、自检闭环、分段缓存、风格包统一色键）借鉴 Frametell，但**代码均为重写或独立实现**。