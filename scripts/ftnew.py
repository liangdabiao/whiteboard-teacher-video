"""新建项目：铺骨架 + 建 engine 链接。

用法
----
  python ftnew.py <项目目录> --title "相对论入门" [--style whiteboard]
                    [--portrait] [--duration 90]

实测坑：examples 目录的 .gitignore 排除了 engine 链接，所以首次必须调 linkProject，
否则后面所有 engine/tools 都会报 "no script.js / 找不到引擎"。

⚠ 关于 linkProject 建的这条 junction（<项目>/engine → skill/engine）——踩过，务必记住：
  · 项目目录**不能建在 skill 目录里面**，否则 engine 成了自己的后代 → 遍历时无限递归。
  · 删项目目录时别用会跟随 junction 的递归删除（MSYS 的 rm -rf 就会跟），
    否则会顺着链接把 skill/engine 连带删掉，再往外还可能删到 skill 之外的源码。
    正确做法：先删掉 <项目>/engine 这个链接本身，再删项目目录。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ftlib import ENGINE, SKILL, SkillError, file_url, run, win  # noqa: E402

STYLES = ["study", "whiteboard", "chalkboard", "warm-story", "tech-dark"]


def engine_call(fn: str, args: list[str]) -> None:
    """调 engine/tools/project.mjs 的导出函数。"""
    proj = ENGINE / "tools" / "project.mjs"
    if not proj.exists():
        raise SkillError(f"引擎缺失：{proj}。先跑 setup。")
    # 引号必须用双引号：bash 单引号会吞掉 file:///D:/ 里的内容，
    # 也会让 Windows 路径的冒号暴露在 eval 里（实测踩过）。
    code = f'import("{file_url(proj)}").then(m=>m.{fn}(...process.argv.slice(1)))'
    run(["node", "-e", code, *args], timeout=180)


def main() -> int:
    ap = argparse.ArgumentParser(description="新建 frametell 视频项目")
    ap.add_argument("project")
    ap.add_argument("--title", required=True)
    ap.add_argument("--style", default="study", choices=STYLES)
    ap.add_argument("--portrait", action="store_true", help="竖屏 1080x1920")
    ap.add_argument("--duration", type=int, default=90, help="目标时长（秒），写进分镜提示")
    args = ap.parse_args()

    project = Path(args.project).resolve()

    # linkProject 会在项目里建 <项目>/engine → skill/engine 的 junction。
    # 项目若在 skill 内部，engine 就成了自己的后代 → 遍历/删除时无限递归。
    if project == SKILL or SKILL in project.parents:
        raise SkillError(
            f"项目目录不能建在 skill 目录里：{project}\n"
            f"  linkProject 会让 <项目>/engine 指回 {SKILL / 'engine'}，形成目录环。\n"
            f"  请换到 skill 之外的路径，例如 D:/films/<片名>"
        )

    project.mkdir(parents=True, exist_ok=True)

    if (project / "script.js").exists():
        print(f"· 项目已存在，保留现有内容：{project}")
    else:
        pages_dir = "pages-portrait" if args.portrait else "pages"
        engine_call("createProject", [win(project), json.dumps(
            {"title": args.title, "style": args.style}, ensure_ascii=False)])
        if args.portrait:
            # 竖版：pages 挪到 pages-portrait/（引擎按 ?portrait 读这个目录）
            src = project / "pages"
            dst = project / pages_dir
            if src.exists():
                dst.mkdir(exist_ok=True)
                for f in src.glob("*.js"):
                    f.rename(dst / f.name)
        print(f"✓ 骨架已铺：{project}")

    # 确保链接在（幂等，Windows 走 junction 免管理员权限）
    engine_call("linkProject", [win(project)])

    # 写一份可用的 script.js 骨架（口播待填）
    sp = project / "script.js"
    if not sp.exists() or sp.stat().st_size < 50:
        sp.write_text(script_skeleton(args.title, args.duration), encoding="utf-8")
        (project / ("pages-portrait" if args.portrait else "pages") / "p01.js").write_text(
            page_skeleton(), encoding="utf-8")

    print(f"""
✓ 项目就绪  {project}
  风格 {args.style}{'（竖屏 1080x1920）' if args.portrait else ''} · 目标 {args.duration}s

  接下来三步：
  1. 写分镜让用户确认 → {project / 'storyboard.json'}
  2. 填口播 → {project / 'script.js'}   （每页 2-3 句，一句一个动画锚点）
  3. 配音 → python {SKILL / 'scripts' / 'ftvoice.py'} {project}
""")
    return 0


def script_skeleton(title: str, duration: int) -> str:
    return f"""/* 口播脚本 —— {title}（目标约 {duration} 秒）
 * 一条 cue = 一个动画锚点。写完跑 ftvoice.py 配音，再用 pages/pNN.js 画画面。
 * 纪律：一页一观点；每页 2-3 句；单句 ≤ 40 字；句尾带标点（决定停顿长短）。
 */
(function (root) {{
  const META = {{
    style: 'study',
    title: '{title}',
    name: '{title}',
    gap: 0.5,
    // voice: {{ speaker: '...' }},   ← ftvoice.py 会自动写入
  }};
  const PAGES = [
    {{ id: 'p01', section: '开场', title: '第一页', cues: [
      '第一句口播。',
      '第二句口播。',
      '{{ t: "第三句，可以多停一会儿。", hold: 0.5 }}',
    ] }},
  ];
  root.SCRIPT = {{ META, PAGES }};
}})(typeof window !== 'undefined' ? window : globalThis);
"""


def page_skeleton() -> str:
    return """/* 页面画面。ENGINE.visual(id, (P) => {...})，P.c(第几句开始)。
 * 纪律：不用 Math.random() / Date.now() / CSS transition；随机走 PV.rng(seed)。
 *      配色只写语义名（ink/blue/redF…）；内容区 x140-1780 / y180-880，y>900 是字幕带。
 */
ENGINE.visual('p01', (P) => {
  const t0 = P.c(0), t1 = P.c(1);
  P.title('页面标题', { accent: 'blue' });
  P.text('第一个元素', { x: 300, y: 400, size: 56, color: 'ink', at: t0, cps: 12 });
  P.box(700, 330, 500, 260, { fill: 'blueF', color: 'blue', at: t1, dur: 0.8, r: 16 });
  P.cam([P.push(P.endT - 1.2, 950, 460, 1.15), P.back(P.endT - 0.3)]);
});
"""


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SkillError as e:
        print(f"\n✗ {e}", file=sys.stderr)
        sys.exit(1)