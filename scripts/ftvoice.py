"""配音：逐句合成 → audio/*.wav → voice.js。

为什么逐句而不是整页一次合成
----------------------------
原项目的 voice 模块是「整页一次合成（语调连贯）→ 用 silencedetect 切回每条 cue」，
这条路依赖 TTS 返回的**字级时间戳**。apiz / edge-tts 都不返回，所以必须改成逐句合成。

代价（已实测确认不会崩）：
  · 整页语调不连贯——句间语气会断，这是逐句合成的固有代价
  · P.cw(i,'词') 退化为按字数比例估算（runtime/timing.js:38 有兜底分支）
收益：
  · 每句时长完全准确（最重要的）
  · 改一句只重合成那一句，缓存友好
  · 不依赖任何厂商的字级时间戳接口

用法
----
  python ftvoice.py <项目目录> [--backend edge|apiz|user] [--voice NAME] [--speed 1.15]
                     [--from 3] [--only p02] [--probe]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ftlib import (  # noqa: E402
    SKILL, SkillError, media_duration, parse_script, run, set_meta_voice,
    strip_silence_edges, to_wav, win, write_voice_js,
)

DEFAULT_SPEED = 1.15

# apiz 音色预设。注意：--voice 要的是 **voice_id**（如 female-chengshu），
# 不是 voices list 里的中文显示名——传显示名会报 "voice id not exist"。
# 全部 56 个中文音色查：apiz voices list --json
APIZ_VOICES = {
    "mature": "female-chengshu",   # 成熟女性，讲解科普最稳（默认）
    "girl": "female-shaonv",       # 少女，偏轻快
    "yujie": "female-yujie",       # 御姐，偏低沉
    "youth": "male-qn-qingse",     # 青涩青年男声
    "sweet": "female-tianmei",     # 甜美女性
    "default": "female-chengshu",
}

# edge 的语音 id 与 apiz 完全不同；预设名在 edge 下映射到对应的微软音色。
# 2026-10 起 speech.platform.bing.com 在部分地区 403，scripts/edge_tts_speak.py
# 改走 api.msedgeservices.com（同一个服务，同一套 token）。
EDGE_HELPER = SKILL / "scripts" / "edge_tts_speak.py"
EDGE_VOICES = {
    "mature": "zh-CN-XiaoxiaoNeural",
    "girl": "zh-CN-XiaoyiNeural",
    "yujie": "zh-CN-XiaoyiNeural",
    "youth": "zh-CN-YunxiNeural",
    "sweet": "zh-CN-XiaoxiaoNeural",
    "default": "zh-CN-XiaoxiaoNeural",
}


# ── 后端适配器 ────────────────────────────────────────────────────

def resolve_voice(backend: str, voice: str | None) -> str:
    """把预设名解析成真实音色 id。

    apiz 只认 voice_id（female-chengshu）；edge 只认微软音色 id
    （zh-CN-XiaoxiaoNeural）。两套 id 不通用，所以预设名按后端分别映射。
    """
    if backend == "edge":
        if voice and voice in EDGE_VOICES:
            return EDGE_VOICES[voice]
        if voice and voice in APIZ_VOICES:
            return EDGE_VOICES.get(voice, EDGE_VOICES["default"])
        return voice or EDGE_VOICES["default"]
    if voice and voice in APIZ_VOICES:
        return APIZ_VOICES[voice]
    return voice or APIZ_VOICES["default"]


def probe_backend(backend: str, voice: str) -> None:
    """发一句探针，提前发现后端不可用——绝不让 agent 跑完整流程才发现配音全废。

    edge：2026-10-22 实测可用 —— 旧域名 speech.platform.bing.com 在部分
    地区 403，但 scripts/edge_tts_speak.py 已改走 api.msedgeservices.com，
    同一个服务、同一套 token，免费且无需 API key。
    """
    # 每个进程用独立的探针文件：并发跑多集时共用 fttts-probe.mp3 会互相删文件，
    # 触发 WinError 32（另一个进程正在使用）。
    tmp = Path(os.environ.get("TEMP", "/tmp")) / f"fttts-probe-{os.getpid()}.mp3"
    try:
        if backend == "apiz":
            if not shutil.which("apiz"):
                raise SkillError("找不到 apiz 命令。装法见 references/tts-backends.md")
            run(["apiz", "speak", "测试", "--model", "speech-2.6-turbo",
                 "--voice", voice, "--output-file", win(tmp)], timeout=90)
        elif backend == "edge":
            run([sys.executable, str(EDGE_HELPER), "--text", "测试", "--voice", voice,
                 "--rate", "+0%", "--out", win(tmp.with_suffix(".mp3"))], timeout=90)
            tmp = tmp.with_suffix(".mp3")
        elif backend == "user":
            return
        if not tmp.exists() or tmp.stat().st_size < 1024:
            raise SkillError("探针没有产出有效音频")
        print(f"  ✓ {backend} 可用（音色 {voice}）")
    except SkillError as e:
        raise SkillError(
            f"✗ TTS 后端 {backend} 不可用：{e}\n\n"
            f"  换一个后端再试：\n"
            f"    python {Path(__file__).name} <项目> --backend edge\n"
            f"    python {Path(__file__).name} <项目> --backend user --user-audio <目录>\n"
            f"  说明见 {SKILL / 'references' / 'tts-backends.md'}"
        ) from e
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def synth_one(backend: str, text: str, voice: str, speed: float, out_mp3: Path) -> Path:
    """合成一句。返回 mp3 路径。"""
    if backend == "apiz":
        run(["apiz", "speak", text, "--model", "speech-2.6-turbo",
             "--voice", voice, "--speed", str(speed), "--output-file", win(out_mp3)],
            timeout=180)
    elif backend == "edge":
        # edge 的语速用 rate 百分比，不是倍数；helper 会改走 api.msedgeservices.com
        pct = int(round((speed - 1.0) * 100))
        rate = f"{pct:+d}%"
        run([sys.executable, str(EDGE_HELPER), "--text", text, "--voice", voice,
             "--rate", rate, "--out", win(out_mp3)], timeout=120)
    elif backend == "user":
        raise SkillError("user 后端不走合成，用 --user-audio <目录>")
    else:
        raise SkillError(f"未知后端 {backend}")
    if not out_mp3.exists() or out_mp3.stat().st_size < 512:
        raise SkillError(f"合成失败或产出为空：{text[:24]}…")
    return out_mp3


# ── 主流程 ────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="whiteboard-teacher-video 配音 → voice.js")
    ap.add_argument("project", help="项目目录（含 script.js）")
    ap.add_argument("--backend", default="edge", choices=["apiz", "edge", "user"],
                    help="TTS 后端（默认 edge：免费、无需 API key，走 api.msedgeservices.com；"
                         "apiz 为付费备选）")
    ap.add_argument("--voice", default=None, help="音色名 / apiz 预设名 / user 时的说明")
    ap.add_argument("--speed", type=float, default=DEFAULT_SPEED, help=f"语速倍数（默认 {DEFAULT_SPEED}）")
    ap.add_argument("--user-audio", default=None,
                    help="user 后端：预录音频目录，按 cue 顺序命名 0.mp3 1.mp3 …")
    ap.add_argument("--only", default=None, help="只配某一页，如 p02")
    ap.add_argument("--from", type=int, default=0, help="从第几条 cue 开始（前缀不动，避免大面积重合成）")
    ap.add_argument("--probe", action="store_true", help="只做后端探针")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    if not (project / "script.js").exists():
        raise SkillError(f"{project} 下没有 script.js")

    voice = resolve_voice(args.backend, args.voice)

    print(f"→ 配音 · 后端 {args.backend} · 音色 {voice} · 语速 {args.speed}")
    if args.probe:
        probe_backend(args.backend, voice)
        return 0
    if args.backend != "user":
        probe_backend(args.backend, voice)

    parsed = parse_script(project / "script.js")
    pages = parsed["pages"]
    if args.only:
        pages = [p for p in pages if p["id"] == args.only]
        if not pages:
            raise SkillError(f"没有这一页：{args.only}")
    if not pages:
        raise SkillError("script.js 里没解析出任何 cue")

    audio_dir = project / "audio"
    audio_dir.mkdir(exist_ok=True)

    # 缓存命中判定：文件名含文本 hash，文本不变即复用
    def cached(page_id: str, idx: int, text: str) -> Path:
        h = hashlib.md5(f"{args.backend}|{text}|{voice}|{args.speed}".encode()).hexdigest()[:10]
        return audio_dir / f"{page_id}-c{idx:02d}-{h}.wav"

    voice_pages: list[list[dict]] = []
    made = reused = 0
    user_files = sorted(Path(args.user_audio).glob("*")) if args.user_audio else []

    for p in parsed["pages"]:
        segs: list[dict] = []
        for i, text in enumerate(p["cues"]):
            wav = cached(p["id"], i, text)
            if wav.exists() and wav.stat().st_size > 512:
                reused += 1
            elif args.backend == "user":
                if i >= len(user_files):
                    raise SkillError(f"user 后端：{args.user_audio} 里只有 {len(user_files)} 个音频，不够 {i + 1} 条")
                mp3 = to_wav(user_files[i], wav.with_suffix(".wav"))
                made += 1
            else:
                mp3 = synth_one(args.backend, text, voice, args.speed, wav.with_suffix(".mp3"))
                to_wav(mp3, wav)          # 引擎吃 wav
                mp3.unlink(missing_ok=True)   # mp3 只是中间产物，留 wav 就够
                made += 1

            dur = media_duration(wav)
            head, tail = strip_silence_edges(wav)
            segs.append({"t": text, "f": f"audio/{wav.name}", "d": round(dur, 3), "o": 0.0})
            flag = "缓存" if wav.exists() and reused else "新合成"
            print(f"  {p['id']} c{i:02d}  {dur:5.2f}s  (头静 {head:.2f}s 尾静 {tail:.2f}s)  {text[:20]}")
        voice_pages.append(segs)

    set_meta_voice(project, voice)
    write_voice_js(project, voice_pages, voice, args.backend)

    # 顺带出字幕（引擎的 script.mjs 会算 srt，但它读的是无配音时间轴，
    # 所以这里自己按 voice.js 的真实时间写）
    write_srt(project, voice_pages)

    total = sum(len(s) for s in voice_pages)
    print(f"\n✓ voice.js 已写入 · {total} 条 cue · 新合成 {made} · 复用 {reused}")
    print(f"  字幕 → {project / 'out' / '字幕.srt'}")
    print(f"  下一步：python {SKILL / 'scripts' / 'ftcheck.py'} {project}")
    return 0


def write_srt(project: Path, voice_pages: list[list[dict]]) -> None:
    """按 voice.js 的真实时间写 SRT。每句一段，与画面 cue 严格对齐。"""
    VOICE = {"lead": 0.2, "comma": 0.18, "stop": 0.4, "pageEnd": 0.3, "gap": 0.3}
    out, t, n = [], 0.0, 1

    def tc(sec: float) -> str:
        ms = int(round(sec * 1000))
        h, m = ms // 3600000, (ms // 60000) % 60
        s = (ms // 1000) % 60
        return f"{h:02d}:{m:02d}:{s:02d},{ms % 1000:03d}"

    for segs in voice_pages:
        t += VOICE["lead"]
        for i, seg in enumerate(segs):
            last = i == len(segs) - 1
            pause = VOICE["pageEnd"] if last else (
                VOICE["stop"] if seg["t"].rstrip().endswith(("。", "？", "！", ".", "?", "!")) else VOICE["comma"])
            start, end = t, t + seg["d"]
            out.append(f"{n}\n{tc(start)} --> {tc(end)}\n{seg['t']}\n")
            n += 1
            t = end + pause
        t += VOICE["gap"]
    srt = project / "out" / "字幕.srt"
    srt.parent.mkdir(exist_ok=True)
    srt.write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SkillError as e:
        print(f"\n✗ {e}", file=sys.stderr)
        sys.exit(1)