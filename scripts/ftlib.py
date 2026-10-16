"""公共库：路径解析、Windows 适配、引擎工具调用、音频探测。

所有脚本的共享底座。这里集中处理 skill 在 Windows 上会踩的坑，
避免每个脚本各写一遍踩坑代码。
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
ENGINE = SKILL / "engine"

# 允许用环境变量覆盖引擎位置（引擎升级、分发测试、多副本场景）。
# 也可以把 skill 整个目录软链到别处而 engine 留在原地。
_env_engine = os.environ.get("FRAMETELL_ENGINE")
if _env_engine and Path(_env_engine).exists():
    ENGINE = Path(_env_engine).resolve()

# ── 进程超时与轮次上限（防止 agent 卡死在一��永不返回的命令上） ──
DEFAULT_TIMEOUT = 900


class SkillError(RuntimeError):
    """skill 的可预期错误：消息直接给用户看，不打堆栈。"""


# ── 路径 ──────────────────────────────────────────────────────────

def win(p: Path | str) -> str:
    """Windows 绝对路径（node / ffmpeg / bash 都要这个形态）。

    实测坑：node 的 import('/d/path') 在 Windows 会被解析成 C:\\d\\path。
    所以凡是拼给 node 看的路径，一律先转成 D:/... 再用 file:/// 包装。
    """
    return str(Path(p).resolve()).replace("\\", "/")


def file_url(p: Path | str) -> str:
    """给 node -e 的 import() 用的 file:// URL。"""
    return "file:///" + win(p)


def engine_tool(name: str) -> Path:
    return ENGINE / "tools" / name


def require_engine() -> Path:
    if not (ENGINE / "tools" / "render.mjs").exists():
        raise SkillError(
            f"引擎未就位（{ENGINE}）。请先运行 setup：\n"
            f"  Windows: powershell -ExecutionPolicy Bypass -File {win(SKILL / 'scripts' / 'setup.ps1')}\n"
            f"  macOS/Linux: python {win(SKILL / 'scripts' / 'setup.py')}"
        )
    return ENGINE


# ── 依赖自检 ──────────────────────────────────────────────────────

@dataclass
class Dep:
    ok: bool
    detail: str


def _nm_candidates() -> list[Path]:
    """引擎可能看到的 node_modules 目录（按优先级）。

    引擎的查找顺序：engine/node_modules → engine/../..  → roughjs 的位置。
    pnpm 的符号链接结构会让这几个路径长得不一样，所以都试一遍。
    """
    out = [ENGINE / "node_modules"]
    out.append(ENGINE.parent / "node_modules")
    out.append(ENGINE.parent.parent / "node_modules")
    try:
        import importlib.util
        spec = importlib.util.find_spec("roughjs")
        if spec and spec.submodule_search_locations:
            out.append(Path(list(spec.submodule_search_locations)[0]).parent)
    except Exception:
        pass
    seen, uniq = set(), []
    for p in out:
        rp = str(p)
        if rp not in seen and p.exists():
            seen.add(rp)
            uniq.append(p)
    return uniq


def check_deps() -> list[Dep]:
    """检查浏览器端依赖是否齐了（字体名做模糊匹配，兼容不同版本）。"""
    need = [
        ("roughjs", ["roughjs/bundled/rough.js"], "手绘线条引擎"),
        ("LXGW WenKai", ["lxgw-wenkai-webfont/lxgwwenkai-regular.css",
                          "lxgw-wenkai-webfont/style.css"], "中文字体（缺了中文变豆腐块）"),
        ("Caveat", ["@fontsource/caveat/500.css"], "英文手写体"),
        ("JetBrains Mono", ["@fontsource/jetbrains-mono/400.css"], "等宽字体"),
    ]
    nm_dirs = _nm_candidates()
    out = []
    for name, rels, why in need:
        hit = next((str(nm / r) for nm in nm_dirs for r in rels if (nm / r).exists()), None)
        if hit:
            out.append(Dep(True, f"{name} ✓"))
        else:
            out.append(Dep(False, f"{name} ✗ 缺失（{why}）· 查找于 {len(nm_dirs)} 个 node_modules"))
    return out


def find_chrome() -> Path | None:
    """引擎的 openStage 会用 playwright-core 找浏览器；这里提前告知缺不缺。"""
    cands = [
        os.environ.get("CHROME_PATH"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
    ]
    for c in cands:
        if c and Path(c).exists():
            return Path(c)
    return None


def ffmpeg() -> str:
    """ffmpeg 路径：优先用引擎装好的 ffmpeg-static，其次系统 PATH。"""
    exe = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    bundled = ENGINE / "node_modules" / "ffmpeg-static" / exe
    if bundled.exists():
        return win(bundled)
    sys_ff = shutil.which("ffmpeg")
    if sys_ff:
        return sys_ff
    raise SkillError("找不到 ffmpeg。请跑 setup 安装依赖，或把 ffmpeg 放进 PATH。")


# ── 命令执行 ──────────────────────────────────────────────────────

def run(cmd: list[str], cwd: Path | None = None, timeout: int = DEFAULT_TIMEOUT,
        quiet: bool = False, check: bool = True) -> str:
    """跑一条命令，返回 stdout。任何 Windows 编码问题都在这里吃掉。"""
    env = os.environ.copy()
    if not quiet:
        print(f"  $ {' '.join(cmd[:3])}…", flush=True)
    try:
        p = subprocess.run(
            cmd, cwd=str(cwd) if cwd else None, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=timeout, env=env,
        )
    except subprocess.TimeoutExpired:
        raise SkillError(f"命令超时（{timeout}s）：{' '.join(cmd[:3])}…")
    if check and p.returncode != 0:
        tail = ((p.stderr or "") + (p.stdout or "")).strip().splitlines()[-12:]
        raise SkillError(f"命令失败（rc={p.returncode}）：{' '.join(cmd[:3])}…\n" + "\n".join(tail))
    return p.stdout or ""


def run_node(args: list[str], cwd: Path, timeout: int = DEFAULT_TIMEOUT,
             check: bool = True) -> str:
    """调用 node 跑引擎工具。cwd 必须是项目目录（引擎从 cwd 找 script.js）。"""
    return run([shutil.which("node") or "node", *args], cwd=cwd, timeout=timeout, check=check)


def run_node_capture(args: list[str], cwd: Path, timeout: int = DEFAULT_TIMEOUT) -> str:
    """跑 node 并返回 stdout + stderr 合并文本，不因非零退出而抛错。

    用途：抓引擎打到 stderr 的浏览器 console 错误（例如 SVG `Expected number "MNaN…"`）。
    这些错误**不抛异常、lint 也查不到**，但对应图形就是画不出来。
    """
    import subprocess
    p = subprocess.run(
        [shutil.which("node") or "node", *args],
        cwd=str(cwd), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
    )
    return (p.stdout or "") + "\n" + (p.stderr or "")


# ── script.js 解析 ────────────────────────────────────────────────

CUE_RE = re.compile(r"'([^']*)'|\"([^\"]*)\"")


def parse_script(js_path: Path) -> dict:
    """从 script.js 抽出 META 和 PAGES。

    不求完备——够驱动配音和质检即可。写脚本请遵守模板里的规范。
    """
    src = js_path.read_text(encoding="utf-8")
    if "PAGES" not in src:
        raise SkillError(f"{js_path} 里找不到 PAGES，确认这是个合法的 script.js")

    meta: dict = {}
    m = re.search(r"const META\s*=\s*\{", src)
    if m:
        depth, i = 1, m.end()
        while i < len(src) and depth:
            if src[i] == "{":
                depth += 1
            elif src[i] == "}":
                depth -= 1
            i += 1
        body = src[m.end(): i - 1]
        mm = re.search(r"style:\s*'([^']*)'", body)
        if mm:
            meta["style"] = mm.group(1)
        mm = re.search(r"name:\s*'([^']*)'", body)
        if mm:
            meta["name"] = mm.group(1)
        mm = re.search(r"title:\s*'([^']*)'", body)
        if mm:
            meta["title"] = mm.group(1)
        meta["_has_voice"] = "voice" in body

    # PAGES：抓每个 { id: 'pNN' ... cues: [ ... ] }
    pages = []
    for pm in re.finditer(r"\{\s*id:\s*'(p\d+)'(.*?)(?=\n\s*\{ id:|\n\s*\];|\Z)", src, re.S):
        pid, rest = pm.group(1), pm.group(2)
        cm = re.search(r"cues:\s*\[(.*?)\]", rest, re.S)
        cues = []
        if cm:
            # 只取字符串与 { t: '...' } 两种形态
            for c in re.finditer(r"\{\s*t:\s*'([^']*)'[^}]*\}|'([^']*)'", cm.group(1)):
                text = c.group(1) or c.group(2)
                if text.strip():
                    cues.append(text)
        sect = re.search(r"section:\s*'([^']*)'", rest)
        pages.append({"id": pid, "section": sect.group(1) if sect else "", "cues": cues})
    return {"meta": meta, "pages": pages}


# ── 音频探测 ──────────────────────────────────────────────────────

def media_duration(file: Path) -> float:
    """音频时长（秒）。从 ffmpeg -i 的输出读，不用 ffprobe。"""
    p = subprocess.run(
        [ffmpeg(), "-hide_banner", "-protocol_whitelist", "file,pipe", "-i", win(file)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", p.stderr or "")
    if not m:
        raise SkillError(f"读不出音频时长：{file}")
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def to_wav(src: Path, dst: Path, rate: int = 24000) -> Path:
    """转成引擎要的 wav（单声道 PCM）。"""
    run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y",
         "-i", win(src), "-ac", "1", "-ar", str(rate), "-c:a", "pcm_s16le", win(dst)],
        timeout=300)
    return dst


def strip_silence_edges(wav: Path) -> tuple[float, float]:
    """用 silencedetect 找首尾静音，返回 (头静音秒, 尾静音秒)。

    edge-tts / apiz 合成的声音首尾常有静音，不裁掉会让画面和声音错位半拍。
    """
    p = subprocess.run(
        [ffmpeg(), "-hide_banner", "-loglevel", "info", "-i", win(wav), "-af",
         "silencedetect=noise=-45dB:d=0.08", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    log = p.stderr or ""
    dur = media_duration(wav)
    head = tail = 0.0
    starts = re.findall(r"silence_start:\s*([\d.]+)", log)
    ends = re.findall(r"silence_end:\s*([\d.]+)", log)
    if starts:
        head = float(starts[0])
    if ends:
        tail = dur - float(ends[-1])
    return max(0.0, head), max(0.0, min(tail, dur - head))


# ── voice.js ──────────────────────────────────────────────────────

VOICE_JS_HEADER = (
    "/* Generated by whiteboard-teacher-video — per-cue narration timing.\n"
    "   No per-character onsets: P.cw() falls back to proportional estimation.\n"
    "   Regenerate after editing any cue text. */\n"
)


def write_voice_js(project: Path, pages: list[list[dict]], speaker: str, provider: str) -> Path:
    """写 voice.js。pages 是每页的 cue 列表，每项 {t,f,d}。"""
    payload = json.dumps(
        {"speaker": speaker, "provider": provider, "pages": pages},
        ensure_ascii=False,
    )
    doc = (
        VOICE_JS_HEADER
        + "SCRIPT.VOICE = "
        + payload
        + ";\n"
    )
    path = project / "voice.js"
    path.write_text(doc, encoding="utf-8")
    return path


def script_has_voice(project: Path) -> bool:
    return (project / "voice.js").exists()


def set_meta_voice(project: Path, speaker: str) -> None:
    """确保 script.js 的 META.voice 存在且 speaker 正确。

    引擎只有在 META.voice 为真时才加载 voice.js（boot.js），否则配音会被忽略。
    """
    sp = project / "script.js"
    src = sp.read_text(encoding="utf-8")
    if "voice:" in src:
        src = re.sub(r"voice:\s*\{[^}]*\}", f"voice: {{ speaker: '{speaker}' }}", src, count=1)
        src = re.sub(r"voice:\s*null", f"voice: {{ speaker: '{speaker}' }}", src, count=1)
    elif "speaker:" in src:
        src = re.sub(r"speaker:\s*'[^']*'", f"speaker: '{speaker}'", src, count=1)
    else:
        src = src.replace("const META = {", f"const META = {{\n    voice: {{ speaker: '{speaker}' }},", 1)
    sp.write_text(src, encoding="utf-8")


def strip_punctuation(t: str) -> str:
    """字幕显示用：去掉句尾软标点（与引擎 subText 一致）。"""
    return re.sub(r"[，。；：、,.;:]+$", "", t).rstrip("—")


def fmt_dur(s: float) -> str:
    return f"{int(s // 60)}:{s % 60:04.1f}"