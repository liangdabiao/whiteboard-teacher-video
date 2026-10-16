# TTS 后端

`ftvoice.py` 的默认后端是 **apiz**。所有后端都走同一套「逐句合成 → 量真实时长 → 写 voice.js」的流程，切换只需一个参数。

## ⚠️ 先看这个：edge-tts 已被封

```
edge-tts --voice zh-CN-XiaoxiaoNeural --text "测试"
aiohttp.client_exceptions.WSServerHandshakeError: 403
wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1?...
```

**微软已对 edge-tts 全域封锁**（`Sec-MS-GEC` 握手被拒）。`ftvoice.py` 保留了这个后端但**不会用作默认**，因为第一次用就会失败。

如果你所在网络能通（极少数情况），可以试：

```bash
python scripts/ftvoice.py <项目> --backend edge --voice zh-CN-YunxiNeural
```

但**先用探针测**：

```bash
python scripts/ftvoice.py <项目> --backend edge --probe
```

---

## apiz（默认 · 实测可用）

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
  --backend apiz \        # apiz | edge | user
  --voice warm \          # 预设名或完整音色名
  --speed 1.15 \          # 语速倍数（apiz 是 1.0-2.0；edge 自动转成百分比）
  --only p02 \            # 只配某一页
  --from 5 \              # 从第 5 条 cue 开始（前缀不动）
  --probe                # 只测后端可用性，不合成
```