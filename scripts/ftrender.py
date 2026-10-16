"""渲染成片 + 成片校验。

引擎本身有分段缓存：改一页只会重渲受影响的片段，靠 sha1(引擎+该页代码+相邻页)
做 key。所以**增量重渲是默认行为**，不用管。

用法
----
  python ftrender.py <项目目录> [--fps 30] [--portrait] [--skip-subs] [--name X]
                     [--no-probe]

产物
----
  out/<name>-无字幕.mp4 / out/<name>-有字幕.mp4（中文项目）
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ftlib import ENGINE, SkillError, find_chrome, run_node  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="whiteboard-teacher-video 渲染")
    ap.add_argument("project")
    ap.add_argument("--fps", type=int, default=30, help="帧率（默认 30；60 更顺但慢一倍）")
    ap.add_argument("--portrait", action="store_true")
    ap.add_argument("--skip-subs", action="store_true", help="不烧字幕（快，只看画面）")
    ap.add_argument("--name", default=None, help="成片文件名（默认取 META.name）")
    ap.add_argument("--no-probe", action="store_true", help="跳过成片校验")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    if not (project / "script.js").exists():
        raise SkillError(f"{project} 下没有 script.js")
    if not find_chrome():
        raise SkillError("找不到 Chrome / Edge，无法渲染。")

    cmd = [str(ENGINE / "tools" / "render.mjs"), "--fps", str(args.fps)]
    if args.portrait:
        cmd.append("--portrait")
    if args.skip_subs:
        cmd.append("--skip-subs")
    if args.name:
        cmd += ["--name", args.name]

    print(f"→ 渲染（{args.fps}fps{'，不烧字幕' if args.skip_subs else ''}）")
    print("  首次渲染较慢；改动单页时靠分段缓存只重渲受影响片段。\n")
    run_node(cmd, cwd=project, timeout=3600)

    # 找成片
    out_dir = project / "out"
    films = sorted(out_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not films:
        raise SkillError("渲染没产出 mp4，检查上面的日志")
    best = films[0]

    if not args.no_probe:
        probe(project, best)

    print(f"""
✓ 成片
  {best}  （{best.stat().st_size / 1e6:.1f} MB）
  {'' if args.skip_subs else f'字幕版：{out_dir / (best.stem.replace("无字幕", "有字幕"))}'}
  字幕：{out_dir / "字幕.srt"}
""")
    return 0


def probe(project: Path, film: Path) -> None:
    """成片自检：时长 + 音视频轨。引擎自己也会校验时长，这里补音轨检查。"""
    from ftlib import ffmpeg, win
    p = subprocess.run(
        [ffmpeg(), "-hide_banner", "-i", win(film)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    log = p.stderr or ""
    import re
    d = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", log)
    v = re.search(r"Video:\s*h264[^,]*,\s*(\d+)x(\d+)", log)
    a = "Audio:" in log
    dur = f"{int(d.group(1)) * 60 + int(d.group(2))}m{d.group(3)}s" if d else "?"
    print(f"  校验：{dur} · {v.group(1)}x{v.group(2)}" if v else f"  校验：{dur}")
    print(f"  音轨：{'有' if a else '无（未配音？）'}")
    if not v:
        raise SkillError("成片没有视频轨，检查渲染日志")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SkillError as e:
        print(f"\n✗ {e}", file=sys.stderr)
        sys.exit(1)