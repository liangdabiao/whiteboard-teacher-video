# TTS 后端

`ftvoice.py` 的默认后端是 **edge**（免费、无需 API key）。所有后端都走同一套「逐句合成 → 量真实时长 → 写 voice.js」的流程，切换只需一个参数。

## edge（免费 · 走新域名）

### 结论（2026-10 实测）

| | |
|---|---|
| 状态 | **可用**，免费、无需余额 |
| 依赖 | Python 包 `edge-tts`（实测 7.2.8），**不需要** `edge-tts` 命令行 |
| 旧域名 | `speech.platform.bing.com/.../readaloud/edge/v1` → 很多地区 403 |
| 新域名 | `wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1` |
| 关键参数 | `TrustedClientToken` 再作为 `Ocp-Apim-Subscription-Key` 传一次 |
| 回退 | 新域名失败自动试旧域名；两个都失败再用 `apiz` |

这不是“绕过鉴权”，而是微软把 Edge Read Aloud 的合成 socket 迁到了新域名；
同一套 `TrustedClientToken` + `Sec-MS-GEC` 仍然有效，只是多一个订阅 key 参数。

### 用法

```bash
# 先用探针确认
python scripts/ftvoice.py <项目> --backend edge --probe

# 正式配音
python scripts/ftvoice.py <项目> --backend edge --voice mature --speed 1.15
```

`ftvoice.py` 会调用 `scripts/edge_tts_speak.py`。这个 helper 做三件事：
1. 把 `edge_tts.communicate.WSS_URL` 临时指向新域名；
2. 带上 `Ocp-Apim-Subscription-Key` 和 Edge 的 User-Agent；
3. 新域名失败时回退旧域名，并把失败原因写进 stderr。

**不要直接用 `edge-tts` CLI**：它的 7.2.8 仍写死旧域名，会 403。
helper 是直接 `import edge_tts` 调 `Communicate.stream()`，所以只依赖包，不依赖入口脚本。

### 预设音色

| 预设名 | edge voice_id | 适合 |
|---|---|---|
| `mature`（默认） | `zh-CN-XiaoxiaoNeural` | 成熟女声，讲解最稳 |
| `sweet` | `zh-CN-XiaoxiaoNeural` | 同上，偏甜 |
| `girl` | `zh-CN-XiaoyiNeural` | 少女，轻快 |
| `yujie` | `zh-CN-XiaoyiNeural` | 偏低沉 |
| `youth` | `zh-CN-YunxiNeural` | 青年男声 |

也可以直接传任意微软音色 id，例如 `zh-CN-YunyangNeural`（男声新闻腔）、
`zh-CN-XiaoxiaoNeural`（女声）。查全部：

```bash
python -m edge_tts --list-voices | findstr zh-CN
```

### 失败时

- 新域名 403：helper 会自动回退旧域名；
- 两个都 403：说明当前网络/地区两条路都不通，换 `--backend apiz`（付费但稳定）；
- `ModuleNotFoundError: edge_tts`：`python -m pip install edge-tts`；
- 音色报 `Invalid voice`：传完整 id（`zh-CN-XiaoxiaoNeural`），不要传中文显示名。

> edge 是逐句合成，句间语调会断；要字级时间戳或更连贯的整段语气，仍建议火山 /
> ElevenLabs / apiz。`P.cw` 在 edge 下按字数比例估算，够用但不精确。

---

## apiz（付费备选 · 实测可用）

CLI 在 PATH 里（`~/.local/bin/apiz`），需要账户余额。

```bash
python scripts/ftvoice.py <项目> --backend apiz --voice mature --speed 1.15
```

**★ `--voice` 要的是 `voice_id`，不是中文显示名**

实测踩过：传 `成熟女性音色` 会报 `HTTP 400 — voice id not exist`。
`apiz voices list` 里 `voice_name`（中文显示名）和 `voice_id`（如 `female-chengshu`）是两个字段，**只能传后者**。

skill 内置预设名（脚本会自动解析成 voice_id）：

| 预设名 | voice_id | 适合 |
|---|---|---|
| `mature` | `female-chengshu` | 成熟女声，**讲解科普最稳**（默认） |
| `girl` | `female-shaonv` | 少女，偏轻快 |
| `yujie` | `female-yujie` | 御姐，偏低沉 |
| `youth` | `male-qn-qingse` | 青涩青年男声 |
| `sweet` | `female-tianmei` | 甜美女声 |

也可以直接传任意 voice_id。查全部 56 个中文音色：

```bash
apiz voices list --json | python -c "
import sys,json
for v in json.load(sys.stdin)['public_voices']:
    if '中文' in str(v.get('tags','')): print(v['voice_id'], v['voice_name'])
"
```

**成本**：1 积分 = 0.01 元。90 秒片子约 380 字。

**检查余额**：

```bash
apiz account balance
```

> ⚠️ **余额不足时所有模型都返回 429**，包括 TTS。跑之前先查余额。

---

## user（用户自带音频 · 零成本零依赖）

你已经有录好的配音，或者不想花钱。

```bash
python scripts/ftvoice.py <项目> --backend user --user-audio D:/my-audios
```

- 目录里的音频按 cue 顺序取，支持 `0.mp3 1.wav 2.mp3 …` 或任意扩展名（**按文件名排序**）
- 数量必须 ≥ cue 总数
- 只支持单声道或任意声道（skill 会转成 24kHz 单声道 wav）

适合：已有播客录音要配画面、课程系列已有配音、想用自己的声音。

---

## 火山 TTS / ElevenLabs（有字级时间戳）

这两个是原项目 `packages/voice` 的原生后端，能返回**字级时间戳**，于是 `P.cw(i, '词')` 可以精确到"念到这个字的瞬间"。

本 skill 的 `ftvoice.py` 目前**没有内置这两个**，但架构上支持——只需在 `synth_one()` 里加一个分支，要求接口返回 `{audio, words}`。需要的话告诉我。

**取舍**：

| | 逐句合成（默认） | 火山 / ElevenLabs |
|---|---|---|
| 整页语调连贯性 | ❌ 句间会断 | ✅ |
| `P.cw` 逐字对齐 | ⚠️ 按字数比例估算 | ✅ 精确 |
| 每句时长准确 | ✅ | ✅ |
| 成本 | 免费/极低 | 付费 |

**大部分场景逐句合成够用**——因为引擎的 `P.cw` 兜底逻辑不会崩，只是不那么精确。

---

## 逐句合成的代价（必须知情）

1. **整页语调不连贯**：每条 cue 独立合成，句间语气会断。短句（≤ 40 字）影响较小；长段落会明显。
2. **`P.cw` 退化为按字数比例估算**：关键数字的同步会有零点几秒偏差，视觉上通常看不出来。
3. **首尾静音**：每句合成通常带几十毫秒静音。`ftvoice.py` 会用 `silencedetect` 量出来并打印出来（`头静 x.xx s 尾静 x.xx s`），但**暂未自动裁剪**——如果你觉得声音发闷，用 ffmpeg 手动裁：

```bash
ffmpeg -i audio/p01-c00.wav -af "silenceremove=start_periods=1:start_duration=0.1:start_threshold=-45dB" out.wav
```

---

## 缓存

文件名含文本 hash：`audio/p01-c00-<md5前10>.wav`

- 文本 + 音色 + 语速不变 → **直接复用**，不重新合成
- 改一句 → 只有那一句重合成
- 改了音色/语速 → 全部重合成

---

## 常用参数

```bash
python scripts/ftvoice.py <项目> \
  --backend edge \         # edge（默认，免费）| apiz（付费）| user（自备音频）
  --voice mature \        # 预设名或完整音色名（edge 见上面的映射）
  --speed 1.15 \          # 语速倍数（apiz 1.0-2.0；edge 自动转成百分比）
  --only p02 \            # 只配某一页
  --from 5 \              # 从第 5 条 cue 开始（前缀不动）
  --probe                # 只测后端可用性，不合成
```