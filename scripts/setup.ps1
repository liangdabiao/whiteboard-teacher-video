# whiteboard-teacher-video 环境安装（Windows PowerShell）
#   powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
# 与 setup.py 等价：取得引擎（GitHub）+ 装依赖（npm 约 130MB）
param([switch]$Force)

$ErrorActionPreference = "Stop"
# 本文件在 <skill>/scripts/ 下，skill 根目录是它的上一层
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Engine = Join-Path $Root "engine"

$Repo = "https://github.com/sitor-ai/frametell.git"
$Sub = "packages/engine"
$Version = "0.7.2"

function Step($n, $msg) { Write-Host "[$n] $msg" -ForegroundColor Yellow }
function HasEngine { Test-Path (Join-Path $Engine "tools\render.mjs") }

Write-Host "`nwhiteboard-teacher-video 安装" -ForegroundColor Cyan
Write-Host "  $Root`n"

# ── 1. 引擎 ──────────────────────────────────────────────────────
Step 1 "视频引擎（来自 GitHub，约 16MB）"

if ((HasEngine) -and (-not $Force)) {
    $n = (Get-ChildItem $Engine -Recurse -File -ErrorAction SilentlyContinue).Count
    Write-Host "    已就位（$n 个文件），跳过" -ForegroundColor DarkGray
}
else {
    # 没有「复用本机已有 frametell」这条捷径：
    # 它必须把 node_modules 建成 junction 指过去，而那正是目录环的来源
    # （表现为 engine 几十万文件、删不掉、还会连带删掉引擎之外的源码）。
    # 引擎与依赖一律各存一份真实副本。
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
            Write-Host "    ✗ 找不到 git。请先装 Git：https://git-scm.com" -ForegroundColor Red
            Write-Host "      或手动下载 $Repo ，把 $Sub 复制到 $Engine" -ForegroundColor Red
            exit 1
        }
        Write-Host "    从 GitHub 获取（只拉 $Sub，约 16MB）…"
        $tmp = Join-Path $Root ".engine-fetch"
        # sparse checkout：避免下载整个 monorepo（含 electron/桌面端，几百 MB）
        git clone --filter=blob:none --no-checkout --depth 1 $Repo $tmp
        if ($LASTEXITCODE -ne 0) { Write-Host "    ✗ clone 失败，可手动下载仓库" -ForegroundColor Red; exit 1 }
        git -C $tmp sparse-checkout init --cone
        git -C $tmp sparse-checkout set $Sub
        git -C $tmp checkout
        if ($LASTEXITCODE -ne 0) { Write-Host "    ✗ sparse checkout 失败" -ForegroundColor Red; exit 1 }
        $src = Join-Path $tmp $Sub

    New-Item -ItemType Directory -Path $Engine -Force | Out-Null
    # /XJ = 不跟随 junction（跟随会把链接目标整棵复制进来，几 MB 能变几 GB）
    robocopy $src $Engine /E /XD node_modules /XJ /NFL /NDL /NJH /NJS /NP | Out-Null
    $n = (Get-ChildItem $Engine -Recurse -File -ErrorAction SilentlyContinue).Count
    Write-Host "    ✓ 引擎就位（$n 个文件，v$Version）" -ForegroundColor Green
    if (Test-Path (Join-Path $Root ".engine-fetch")) {
        Remove-Item (Join-Path $Root ".engine-fetch") -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# ── 2. 依赖 ──────────────────────────────────────────────────────
Step 2 "第三方依赖（约 130MB）"
$Nm = Join-Path $Root "node_modules"

if (Test-Path (Join-Path $Nm "roughjs\bundled\rough.js")) {
    Write-Host "    已就位，跳过" -ForegroundColor DarkGray
}
else {
    # 只装一份真实目录，放 <skill>/node_modules。
    # 引擎会按 engine/node_modules → engine/.. 的顺序自己找到它，不需要链接。
    Write-Host "    npm install（约 130MB，1–3 分钟）…"
    # package.json 在 skill 根目录，必须在根目录下跑，否则 node_modules 装错地方
    Push-Location $Root
    try {
        npm install --no-audit --no-fund 2>&1 | Out-Null
    } finally {
        Pop-Location
    }
    if (-not (Test-Path (Join-Path $Nm "roughjs"))) {
        Write-Host "    ✗ npm install 失败。国内网络可换镜像：" -ForegroundColor Red
        Write-Host "      npm config set registry https://registry.npmmirror.com" -ForegroundColor Red
        exit 1
    }
    Write-Host "    ✓ 依赖就位" -ForegroundColor Green
}

# 清掉历史遗留的 engine/node_modules 链接：
# 它是目录环的入口，删 engine 时会顺着它钻进别处把源码连带删光。
$EngNm = Join-Path $Engine "node_modules"
$link = Get-Item -LiteralPath $EngNm -Force -ErrorAction SilentlyContinue
if ($link -and ($link.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
    # 只删链接本身，不动它指向的目标
    $link.Delete()
    Write-Host "    ✓ 已移除历史遗留的 engine/node_modules 链接" -ForegroundColor Green
}

# ── 3. 环境检查 ──────────────────────────────────────────────────
Step 3 "环境检查"
$chrome = @(
    "$env:PROGRAMFILES\Google\Chrome\Application\chrome.exe",
    "${env:PROGRAMFILES(X86)}\Google\Chrome\Application\chrome.exe",
    "${env:PROGRAMFILES(X86)}\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($chrome) { Write-Host "    ✓ 浏览器 $chrome" -ForegroundColor Green }
else { Write-Host "    ✗ 没找到 Chrome/Edge，渲染需要它" -ForegroundColor Red }

if ((Test-Path (Join-Path $Nm "ffmpeg-static\ffmpeg.exe")) -or (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "    ✓ ffmpeg 就绪" -ForegroundColor Green
} else { Write-Host "    ✗ ffmpeg 缺失" -ForegroundColor Red }

if (Get-Command apiz -ErrorAction SilentlyContinue) { Write-Host "    ✓ TTS 后端 apiz" -ForegroundColor Green }
else { Write-Host "    ⚠ 没有 apiz，配音需另配后端（见 references/tts-backends.md）" -ForegroundColor Yellow }
if (Get-Command edge-tts -ErrorAction SilentlyContinue) {
    Write-Host "    ⚠ edge-tts 已装，但微软已 403 封锁，先跑探针再用" -ForegroundColor Yellow
}
if (Get-Command node -ErrorAction SilentlyContinue) {
    Write-Host "    ✓ Node.js $(node -v)" -ForegroundColor Green
} else { Write-Host "    ✗ 找不到 node" -ForegroundColor Red }

Write-Host "`n✓ 就绪  $Root" -ForegroundColor Green
Write-Host "  引擎 v$Version · 上游 https://github.com/sitor-ai/frametell"
Write-Host @"

下一步：
  python scripts/ftnew.py D:/films/my-film --title "标题" --style whiteboard
  # 填 script.js → ftvoice.py → 画 pages/ → ftcheck.py → ftrender.py

细节见 SKILL.md 与 references/
"@ -ForegroundColor Gray