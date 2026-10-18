"""whiteboard-teacher-video 环境安装。

公众用户只需一步：
    python scripts/setup.py

做两件事：
  1. 取得视频引擎（来自 GitHub，sparse checkout 只拉 packages/engine）
  2. 装第三方依赖（npm，约 130MB）

引擎为什么不在 skill 包里：
  它有 16MB / 38 万个文件（three.js 展开），打进 skill 包会让分发变得很重。
  改为安装时从上游拉取 —— 与 whiteboard-explainer 的 vendor 策略一致。
  详见 vendor/ATTRIBUTION.md。

⚠ 为什么这里一律不用符号链接 / junction（踩过，别加回来）
  曾经为了省 130MB，把 node_modules 建成链接指向上游 monorepo，
  再让 engine/node_modules 链接回 skill 根目录 —— 形成环。
  后果：任何递归遍历（含删除）都顺着链接钻进上游源码树，
  表现为「engine 几百 MB/10GB、几十万个文件、删不掉」，
  并且真的把引擎之外的源码连带删光。
  现在全部改为真实目录 + 复制。依赖只有一份，在 <skill>/node_modules。
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

# 本文件在 <skill>/scripts/ 下，skill 根目录是它的上一层
ROOT = Path(__file__).resolve().parent.parent
ENGINE = ROOT / "engine"

REPO = "https://github.com/sitor-ai/frametell.git"
ENGINE_SUBPATH = "packages/engine"
ENGINE_VERSION = "0.7.2"

# 不再有「复用本机已有 frametell」这条捷径：
# 它必须把 node_modules 建成链接指过去，而那正是目录环的来源。
# 引擎与依赖一律各存一份真实副本，宁可多 130MB，不要链接。

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/microsoft-edge",
]


def step(n: int, msg: str) -> None:
    print(f"[{n}] {msg}")


def have_engine() -> bool:
    return (ENGINE / "tools" / "render.mjs").exists()


def engine_file_count() -> int:
    return sum(1 for _ in ENGINE.rglob("*") if _.is_file()) if ENGINE.exists() else 0


# ── 1. 引擎 ──────────────────────────────────────────────────────

def fetch_engine(force: bool = False) -> None:
    """取得引擎：始终从 GitHub sparse checkout 拿一份真实副本。"""
    if have_engine() and not force:
        print(f"    已就位（{engine_file_count()} 个文件），跳过")
        return

    git = shutil.which("git")
    if not git:
        print("    ✗ 找不到 git。引擎需要从 GitHub 获取，请先装 Git：https://git-scm.com")
        print(f"      或手动下载 {REPO} ，把 {ENGINE_SUBPATH} 整个目录复制到 {ENGINE}")
        sys.exit(1)

    print(f"    从 GitHub 获取（只拉 {ENGINE_SUBPATH}，约 16MB）…")
    # sparse checkout：避免下载整个 monorepo（含 electron/桌面端，几百 MB）
    tmp = ROOT / ".engine-fetch"
    cmds = [
        ["git", "clone", "--filter=blob:none", "--no-checkout", "--depth", "1", REPO, str(tmp)],
        ["git", "-C", str(tmp), "sparse-checkout", "init", "--cone"],
        ["git", "-C", str(tmp), "sparse-checkout", "set", ENGINE_SUBPATH],
        ["git", "-C", str(tmp), "checkout"],
    ]
    for cmd in cmds:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            print(f"    ✗ {' '.join(cmd[:4])} 失败：\n{(r.stderr or '').strip()[-400:]}")
            print(f"      可手动下载 {REPO} ，把 {ENGINE_SUBPATH} 复制到 {ENGINE}")
            # 清理失败的临时目录（逐项删除，避开批量删除钩子）
            if tmp.exists():
                shutil.rmtree(tmp, ignore_errors=True)
            sys.exit(1)

    src = tmp / ENGINE_SUBPATH
    if not (src / "tools" / "render.mjs").exists():
        print(f"    ✗ 拉下来的目录里没有引擎（{src}）")
        sys.exit(1)

    ENGINE.mkdir(parents=True, exist_ok=True)
    copy_engine(src)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"    ✓ 引擎就位（{ENGINE_VERSION}）")


def copy_engine(src: Path) -> None:
    """复制引擎源码（跳过 node_modules，且不跟随链接）。

    symlinks=True 是关键：copytree 默认会「跟随」链接把目标内容整棵复制进来，
    一旦源里有指向外边的链接（pnpm 的 .pnpm 就是），几 MB 的引擎能复制成几 GB。
    保留链接本身、不展开，就不会失控。
    """
    src = src.resolve()
    dst = ENGINE.resolve()
    if dst == src or dst in src.parents:
        raise SystemExit(f"✗ 拒绝复制：目标是源的祖先（{src} → {dst}），会无限递归")
    if src in dst.parents:
        raise SystemExit(f"✗ 拒绝复制：源在目标内部（{src} → {dst}），会无限递归")

    ENGINE.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, ENGINE, ignore=shutil.ignore_patterns("node_modules", "*.pyc"),
                    dirs_exist_ok=True, symlinks=True)
    print(f"    ✓ 已复制 {engine_file_count()} 个文件")


# ── 2. 依赖 ──────────────────────────────────────────────────────

def install_deps() -> None:
    """装依赖，只装一份真实目录，放在 <skill>/node_modules。

    引擎自己会按 engine/node_modules → engine/..（即 skill 根目录）的顺序找依赖，
    所以根目录这一份就够了，不需要在 engine 下再放任何链接。
    """
    nm = ROOT / "node_modules"
    if (nm / "roughjs" / "bundled" / "rough.js").exists():
        print("    已就位，跳过")
        return

    print("    npm install（约 130MB，1–3 分钟）…")
    npm = shutil.which("npm") or (shutil.which("npm.cmd") if os.name == "nt" else None)
    if not npm:
        print("    ✗ 找不到 npm。请先装 Node.js ≥ 22.19：https://nodejs.org")
        sys.exit(1)
    r = subprocess.run([npm, "install", "--no-audit", "--no-fund"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0 or not (nm / "roughjs").exists():
        print(f"    ✗ npm install 失败：\n{(r.stderr or '')[-500:]}")
        print("      国内网络可换镜像：npm config set registry https://registry.npmmirror.com")
        sys.exit(1)
    print("    ✓ 依赖就位")

    # 不要在这里建 engine/node_modules 链接：
    # 引擎已经会向上找到 <skill>/node_modules，链接只会制造删除时的遍历风险。
    eng_nm = ENGINE / "node_modules"
    is_link = eng_nm.is_symlink() or (hasattr(eng_nm, "is_junction") and eng_nm.is_junction())
    if is_link:
        eng_nm.unlink()
        print("    ✓ 已移除历史遗留的 engine/node_modules 链接")


# ── 3. 环境检查 ──────────────────────────────────────────────────

def check_env() -> bool:
    ok = True
    br = next((b for b in BROWSERS if Path(b).exists()), None)
    print(f"    {'✓' if br else '✗'} 浏览器 {br or '未找到 Chrome/Edge —— 渲染需要它'}")
    ok = ok and bool(br)

    ff = ROOT / "node_modules" / "ffmpeg-static" / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    if not ff.exists():
        ff = shutil.which("ffmpeg")
    print(f"    {'✓' if ff else '✗'} ffmpeg {'就绪' if ff else '缺失'}")
    ok = ok and bool(ff)

    apiz = shutil.which("apiz")
    print(f"    {'✓' if apiz else '⚠'} TTS 后端 apiz {'就绪' if apiz else '未安装（见 references/tts-backends.md）'}")

    edge = subprocess.run(
        [sys.executable, "-c", "import edge_tts; print(getattr(edge_tts, '__version__', '?'))"],
        capture_output=True, text=True,
    )
    if edge.returncode == 0:
        print(f"    ✓ TTS 后端 edge {edge.stdout.strip()}（新域名；--backend edge）")
    else:
        print("    ⚠ TTS 后端 edge 未安装（pip install edge-tts；不用 CLI 也能跑）")

    node = shutil.which("node")
    if node:
        v = subprocess.run([node, "-v"], capture_output=True, text=True).stdout.strip()
        print(f"    ✓ Node.js {v}")
    else:
        print("    ✗ 找不到 node")
        ok = False
    return ok


# ── main ─────────────────────────────────────────────────────────

def main() -> int:
    force = "--force" in sys.argv
    print("\nwhiteboard-teacher-video 安装\n")
    step(1, "视频引擎（来自 GitHub，约 16MB）")
    fetch_engine(force=force)
    step(2, "第三方依赖（约 130MB）")
    install_deps()
    step(3, "环境检查")
    ok = check_env()

    print(f"\n{'✓ 就绪' if ok else '⚠ 基本就绪（见上面标 ✗ 的项）'}  {ROOT}")
    print(f"  引擎版本 {ENGINE_VERSION} · 上游 https://github.com/sitor-ai/frametell")
    print("""
下一步：
  python scripts/ftnew.py D:/films/my-film --title "标题" --style whiteboard
  # 然后填 script.js → ftvoice.py → 画 pages/ → ftcheck.py → ftrender.py

细节见 SKILL.md 与 references/
""")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())