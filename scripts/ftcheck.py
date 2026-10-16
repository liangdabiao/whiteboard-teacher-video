"""质检：lint（机器判）+ 逐页拼图（给 agent 看）+ 结构化报告。

这是 whiteboard-teacher-video 相对原项目最大的增量：
原项目的 agent 通过 bash 拿 base64 截图，本脚本把拼图**写成文件**，
agent 可以直接用 Read 工具打开看图，然后定点修改。

用法
----
  python ftcheck.py <项目目录> [--only p01,p02] [--times 4] [--no-sheets]

产物
----
  out/sheets/pNN.jpg      拼图（每页取若干时刻横向拼）
  out/lint.json            机器检查结果
  stdout                   人类/agent 可读摘要
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ftlib import ENGINE, SkillError, find_chrome, run_node, run_node_capture  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="whiteboard-teacher-video 质检")
    ap.add_argument("project")
    ap.add_argument("--only", default=None, help="只查某几页，如 p01,p02")
    ap.add_argument("--times", type=int, default=4, help="每页取几个时刻（默认 4）")
    ap.add_argument("--no-sheets", action="store_true", help="只跑 lint，不出拼图")
    ap.add_argument("--determinism", action="store_true", help="额外做确定性检查（同一时刻渲染两次比对）")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    if not (project / "script.js").exists():
        raise SkillError(f"{project} 下没有 script.js")

    chrome = find_chrome()
    if not chrome:
        raise SkillError("找不到 Chrome / Edge。渲染需要本机装有 Chrome 系浏览器。")

    only = f"--only={args.only}" if args.only else ""
    report: dict = {"project": str(project), "lint": [], "sheets": {}, "warnings": []}

    # ── 1. 时间轴：先确认配音是否就位、每页多长 ──
    print("→ 时间轴")
    tl = run_node([str(ENGINE / "tools" / "pages.mjs"), "--json"], cwd=project, check=False)
    try:
        data = json.loads(tl)
        report["voiced"] = data.get("voiced")
        report["duration"] = data.get("duration")
        pages = data.get("pages", [])
        for p in pages:
            print(f"  {p['id']}  {p['start']}s → {p['end']}s（讲完 {p['speechEnd']}s）  {len(p['cues'])} 句")
    except json.JSONDecodeError:
        report["warnings"].append("pages.mjs 输出无法解析，跳过时间轴检查")

    # ── 2. lint：机器能判的问题 ──
    print("→ lint（确定性检查）")
    cmd = [str(ENGINE / "tools" / "lint.mjs")]
    if only:
        cmd.append(f"--only={args.only}")
    if args.determinism:
        cmd.append("--determinism")
    cmd.append("--json")
    out = run_node(cmd, cwd=project, check=False)
    issues: list[dict] = []
    try:
        issues = json.loads(out)
        report["lint"] = issues
        errors = [i for i in issues if i.get("level") in ("error", "err")]
        warns = [i for i in issues if i.get("level") not in ("error", "err")]
        if not issues:
            print("  ✓ 无布局问题")
        for i in issues[:20]:
            mark = "✗" if i in errors else "·"
            print(f"  {mark} {i.get('page', '?')}  {i.get('kind', '')}  {i.get('msg', '')}")
        if len(issues) > 20:
            print(f"  … 还有 {len(issues) - 20} 条，见 out/lint.json")
    except json.JSONDecodeError:
        print(f"  · lint 输出非 JSON（可能有页面报错）：{out.strip()[:300]}")
        report["warnings"].append("lint 输出异常")

    (project / "out").mkdir(exist_ok=True)
    (project / "out" / "lint.json").write_text(
        json.dumps(issues, ensure_ascii=False, indent=1), encoding="utf-8")

    # ── 3. 逐页拼图：agent 用来看 ──
    # 注意：snap.mjs 的 --sheet 只收**文件名**，产物固定落在 out/snap/<name>.jpg
    sheets: dict[str, str] = {}
    nan_pages: list[str] = []
    if not args.no_sheets and pages:
        print("→ 拼图（agent 直接看图改）")
        for p in pages:
            pid = p["id"]
            if args.only and pid not in args.only.split(","):
                continue
            # 每页取 speechEnd 附近若干时刻，画面最完整
            span = max(1.0, p["speechEnd"] - p["start"])
            picks = [p["start"] + span * (i + 1) / (args.times + 1) for i in range(args.times)]
            # stdout/stderr 一起抓：**NaN 是 lint 查不到的致命伤**
            # （例如 P.cross 把配置对象当尺寸传 → sz/2 = NaN → 图形静默消失）
            proc = run_node_capture([str(ENGINE / "tools" / "snap.mjs"), "--only", pid, "--sheet", f"{pid}"]
                                    + [f"{t:.2f}" for t in picks], cwd=project)
            if "NaN" in proc:
                nan_pages.append(pid)
            produced = project / "out" / "snap" / f"{pid}.jpg"
            if produced.exists():
                sheets[pid] = str(produced)
                flag = f"  ⚠ 含 NaN×{proc.count('NaN')}" if pid in nan_pages else ""
                print(f"  ✓ {pid} → out/snap/{pid}.jpg{flag}")
            else:
                print(f"  ✗ {pid} 拼图未产出")

    report["sheets"] = sheets
    report["nan_pages"] = nan_pages
    (project / "out" / "check-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    n_err = len([i for i in report["lint"] if i.get("level") in ("error", "err")])
    nan_note = ""
    if nan_pages:
        nan_note = f"\n  ⚠ NaN：{', '.join(nan_pages)} ← lint 查不到，但这些图形画不出来"
        nan_note += "\n     多半是 P.check/P.cross 把配置对象当尺寸传，或 liveRough 回调参数遮蔽了变量"
        print(nan_note)
    print(f"""
{'=' * 56}
质检完成
  时长 {report.get('duration', '?')}s · 配音 {'已就位' if report.get('voiced') else '未配（画面仍可渲染）'}
  lint：{n_err} 个错误 / {len(report['lint']) - n_err} 个提醒
  拼图：{len(sheets)} 张 → {project / 'out' / 'snap'}{nan_note}
  报告：{project / 'out' / 'check-report.json'}
{'=' * 56}
★ 下一步：用 Read 工具逐页打开 out/snap/pNN.jpg 看图
  （lint 只管硬错误，构图好不好看它不管）
  全绿后 → python {Path(__file__).parent / 'ftrender.py'} {project}
""")
    return 1 if (n_err or nan_pages) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SkillError as e:
        print(f"\n✗ {e}", file=sys.stderr)
        sys.exit(2)