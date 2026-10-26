"""生成 / 更新「技能介绍视频」项目进度表。

用法
----
  python scripts/progress.py                       # 扫默认素材目录，输出 D:/films/PROGRESS.md
  python scripts/progress.py --src <素材目录> --films <成片目录> --out <输出md>

为什么要有这个脚本
------------------
项目有 138 个 md，手工维护进度表必然记错。这个脚本每次都从**事实**重新算：
  · 素材：<src>/*.md（排除 4 个非项目文件）
  · 仓库地址：md 里的「代码仓库：」行优先；没有就用 .workbuddy_meta.json 的 link
  · 完成状态：<films>/<项目目录>/out/*-有字幕.mp4 是否存在

作者：liangdabiao
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 素材目录里不是「项目介绍」的 md
NOT_PROJECTS = {"ALL-MERGED", "README", "MISSING-DOCS", "_aefs_readme_backup"}

# 明确不做（2026-10-22 用户确认）。排除出统计，不计入「待做」。
# 原因：这三个在 github_repos_over_3_stars.md 的 143 个仓库里找不到确定对应的项目。
EXCLUDE = {
    "game-gameability",            # 只有 boardgame-io-skill / go-game-ai，均非「游戏性验证」
    "wechat-writer",               # 只有 wechat-article-remotion / liurun-bookwriter-skills，均非「写稿+配图」
    "ian-xiaohei-illustrations",   # 只有 directing-xiaohei-videos（动画，非配图），功能对不上
}

# 仓库地址人工确认表：md 里没写「代码仓库」、且名字与仓库名不一致时用。
# 值 = (地址, 确认依据)。依据写清楚，下次不用重新查。
REPO_OVERRIDE = {
    "glm-5.3-flash-vision-video-rag": (
        "https://github.com/liangdabiao/glm-5.3-flash-vision-rag",
        "清单简介：三个 GLM 视觉技能总览，视频 RAG 是其中之一"),
    "pindou-pattern": (
        "https://github.com/liangdabiao/perler-beads-skill",
        "清单简介原文：拼豆图纸生成器（pindou-perlerBeads-skill）"),
    "talking-head-remotion": (
        "https://github.com/liangdabiao/video-skills-toolkit/tree/main/skills/talking-head-remotion",
        "video-skills-toolkit 仓库内子目录，与 md 同名"),
    "mathigon-skill": (
        "https://github.com/liangdabiao/textbooks",
        "清单简介：我制作了 mathigon textbooks skill（名字差异大，制作前再核一次）"),
}

# md 文件名 → 成片目录名（两者不一致时才需要登记）
# 新增片子时**不需要**改这里：脚本会按仓库名/标题自动匹配，只有自动匹配失败才要登记。
ALIAS = {
    "geometry-math-proof-remotion": "math-proof",
    "xhs-business-validator": "xhs-validator",
    "deepseek-v4-flash-vision-video-rag": "deepseek-video-rag",
    "glm-ecom-video-seedance-prompt": "ecom-video-seedance-prompt",
    # 2026-10-23 补登（成片目录名与 md 名不同，之前漏认导致重复出现在待做里）
    "glm-5.3-flash-vision-video-rag": "glm-vision-video-rag",
    "deepseek-v4-flash-vision-rag": "deepseek-pdf-rag",
    "glm-5.3-flash-vision-rag": "glm-vision-pdf-rag",
    "simple-review-analyzer": "review-analyzer",
    "reddit-business-idea-validator": "reddit-idea-validator",
    "mathigon-skill": "mathigon-skill",
    "brickMosaic": "brick-mosaic",
    # 2026-10-23 视频化系列（Remotion 族），成片目录用连字符
    "XHS_Business_Idea_Validator": "xhs-idea-validator-orig",
    # 2026-10-23 第四批（5 页版）
    "directing-xiaohei-videos": "directing-xiaohei",
    "seedance2-storyboard": "seedance2-storyboard",
    "ecom-details-image": "ecom-details-image",
    "sif-amazon-research": "sif-amazon-research",
    "langgraph-multi-agent-rag-customer-support": "langgraph-cs",
    "multimodal-rag": "multimodal-rag",
    "fashion-ai": "fashion-ai",
}

# ── 系列片：多个 md 合成一条视频 ───────────────────────────────────────────
# 为什么要有：很多 md 其实是同一个仓库的多个子技能（edulab 下 7 个、
# amazon-sorftime 下 9 个），或同一套模板的多个变体（claudesdk-* 7 个）。
# 给它们各做一条 8 页片，内容会高度重复、观众也记不住区别。
# 合成一条「系列片」讲清共性和每个成员干什么，信息密度更高，成本降一个数量级。
#
# 字段：
#   slug    成片目录名（D:/films/<slug>）
#   title   片名
#   repo    仓库地址（同仓库）或 None（同模板不同仓库 → 地址页列 repo_list）
#   repo_list 多仓库时列在地址页上的清单（[名称, 地址] 或 [名称, 地址, 子路径]）
#   covers  覆盖的 md 文件名（不含 .md）
#   style   风格
SERIES = [
    {
        "slug": "series-edulab",
        "title": "edulab · 数学与理科交互课件合集",
        "repo": "https://github.com/liangdabiao/edulab",
        "style": "chalkboard",
        # 注意：edu-analytic-geometry 已单独出片（D:/films/edu-analytic-geometry），
        # 不算进本系列的覆盖，避免重复计数；系列片里可以口头带一句它。
        "covers": ["edu-plane-geometry", "edu-solid-geometry",
                   "edu-chem-reaction", "edu-chem-tutorial", "edu-physics",
                   "edu-physics-3d", "edu-sci-viz"],
    },
    {
        "slug": "series-amazon-sorftime",
        "title": "amazon-sorftime · 亚马逊选品研究技能包",
        "repo": "https://github.com/liangdabiao/amazon-sorftime-research-MCP-skill",
        "style": "tech-dark",
        "covers": ["amazon-sorftime-research-mcp-skill", "amazon-analyse", "amazon-listing-builder",
                   "category-selection", "keyword-research", "product-research",
                   "review-analysis", "sellersprite-amazon-research", "xiyou-insight"],
    },
    {
        "slug": "series-claudesdk",
        "title": "claudesdk · 一套 SDK 做七个对话工具",
        "repo": None,
        "repo_list": [
            ("claudesdk-skill", "https://github.com/liangdabiao/claudesdk-skill"),
            ("claudesdk-amazon-chat", "https://github.com/liangdabiao/claudesdk-amazon-chat"),
            ("claudesdk-exa-chat", "https://github.com/liangdabiao/claudesdk-exa-chat"),
            ("claudesdk-seedance-chat", "https://github.com/liangdabiao/claudesdk-seedance-chat"),
        ],
        "style": "tech-dark",
        "covers": ["claudesdk-skill", "claudesdk-amazon-chat", "claudesdk-amazon-skills-chat",
                   "claudesdk-ecom-image-chat", "claudesdk-exa-chat", "claudesdk-financial-chart-chat",
                   "claudesdk-market-insight-chat", "claudesdk-seedance-chat"],
    },
    {
        "slug": "series-apiz",
        "title": "apiz · 一个命令行管住所有 AI 能力",
        "repo": "https://github.com/liangdabiao/apiz-skill",
        "style": "tech-dark",
        "covers": ["apiz", "apiz-use"],
    },
    {
        "slug": "series-geo",
        "title": "GEO 内容优化 · 两个技能一条链路",
        "repo": "https://github.com/liangdabiao/GEO-Content-Optimizer-Skill",
        "style": "whiteboard",
        "covers": ["geo-content-optimizer", "geo-optimizer"],
    },
    {
        "slug": "series-exa",
        "title": "exa-research · 公司调研与外贸调研",
        "repo": "https://github.com/liangdabiao/exa-research-mcp-skill",
        "style": "tech-dark",
        "covers": ["exa-company-research", "exa-foreign-trade-research"],
    },
    {
        "slug": "series-hyperframes",
        "title": "hyperframes · 视频规格与修复",
        "repo": "https://github.com/liangdabiao/hyperframes-fix",
        "style": "tech-dark",
        "covers": ["hyperframes-fix", "hyperframes-video-spec-builder"],
    },
    {
        "slug": "series-llm-wiki",
        "title": "llm-wiki · 用 Agent SDK 做 agentic RAG",
        "repo": "https://github.com/liangdabiao/llm-wiki-claude-agent-sdk-agentic-rag",
        "style": "tech-dark",
        "covers": ["llm-wiki-claude-agent-sdk-agentic-rag", "claude-agent-sdk"],
    },
    # ── 2026-10-23 第五批：同族合并系列片
    {
        "slug": "series-deep-research",
        "title": "Deep Research · 四种搭法",
        "repo": None,
        "repo_list": [
            ("Claude-Code-Deep-Research-main", "https://github.com/liangdabiao/Claude-Code-Deep-Research-main"),
            ("Claude-Code-Stock-Deep-Research-Agent", "https://github.com/liangdabiao/Claude-Code-Stock-Deep-Research-Agent"),
            ("simple_claude_deep_research_agent", "https://github.com/liangdabiao/simple_claude_deep_research_agent"),
            ("deep_search_write", "https://github.com/liangdabiao/deep_search_write"),
        ],
        "style": "tech-dark",
        "covers": ["claude-code-deep-research-main", "claude-code-stock-deep-research-agent",
                   "simple-claude-deep-research-agent", "deep-search-write"],
    },
    {
        "slug": "series-invest-agent",
        "title": "投资 Agent · 四个多智能体方案",
        "repo": None,
        "repo_list": [
            ("easy_investment_Agent_crewai", "https://github.com/liangdabiao/easy_investment_Agent_crewai"),
            ("investment_Agent_langgraph_crewai", "https://github.com/liangdabiao/investment_Agent_langgraph_crewai"),
            ("crewai_stock_analysis_system", "https://github.com/liangdabiao/crewai_stock_analysis_system"),
            ("autogen-financial-analysis", "https://github.com/liangdabiao/autogen-financial-analysis"),
        ],
        "style": "tech-dark",
        "covers": ["easy-investment-agent-crewai", "investment-agent-langgraph-crewai",
                   "crewai-stock-analysis-system", "autogen-financial-analysis"],
    },
    {
        "slug": "series-demand-insight",
        "title": "需求洞察 · AI 挖商机",
        "repo": None,
        "repo_list": [
            ("ai-investor", "https://github.com/liangdabiao/ai-investor"),
            ("SeekMoney-ai", "https://github.com/liangdabiao/SeekMoney-ai"),
        ],
        "style": "whiteboard",
        "covers": ["ai-investor", "seekmoney-ai"],
    },
    {
        "slug": "series-cli-workflow",
        "title": "CLI 工作流 · 把办公软件变成 AI 中枢",
        "repo": None,
        "repo_list": [
            ("lark-workflow-feishu-cli", "https://github.com/liangdabiao/lark-workflow-feishu-cli"),
            ("lark-crm-feishu-cli", "https://github.com/liangdabiao/lark-crm-feishu-cli"),
            ("dingtalk-cli-workflow", "https://github.com/liangdabiao/dingtalk-cli-workflow"),
        ],
        "style": "tech-dark",
        "covers": ["lark-workflow-feishu-cli", "lark-crm-feishu-cli", "dingtalk-cli-workflow"],
    },
    {
        "slug": "series-kefu",
        "title": "智能客服 · 两套方案",
        "repo": None,
        "repo_list": [
            ("SKILL-kefu", "https://github.com/liangdabiao/SKILL-kefu"),
            ("wordpress_kefu_ai_agent", "https://github.com/liangdabiao/wordpress_kefu_ai_agent"),
        ],
        "style": "study",
        "covers": ["skill-kefu", "wordpress-kefu-ai-agent"],
    },
    # ── 2026-10-23 第六批
    {
        "slug": "series-resume",
        "title": "简历筛选 · 两个方向",
        "repo": None,
        "repo_list": [
            ("resume-matcher-agent-cn", "https://github.com/liangdabiao/resume-matcher-agent-cn"),
            ("LLM-Agent-Resume", "https://github.com/liangdabiao/LLM-Agent-Resume"),
        ],
        "style": "study",
        "covers": ["resume-matcher-agent-cn", "llm-agent-resume"],
    },
    {
        "slug": "series-crm",
        "title": "对话式 CRM · 三种形态",
        "repo": None,
        "repo_list": [
            ("monica-crm-claude-skill", "https://github.com/liangdabiao/monica-crm-claude-skill"),
            ("wecomcli_crm", "https://github.com/liangdabiao/wecomcli_crm"),
            ("lark-crm-feishu-cli", "https://github.com/liangdabiao/lark-crm-feishu-cli"),
        ],
        "style": "tech-dark",
        "covers": ["monica-crm-claude-skill", "wecomcli-crm", "lark-crm-feishu-cli"],
    },
    {
        "slug": "series-ecom-image",
        "title": "电商生图 · 三种形态",
        "repo": None,
        "repo_list": [
            ("ecom-details-image", "https://github.com/liangdabiao/ecom-details-image"),
            ("ecom-details-image-ui", "https://github.com/liangdabiao/ecom-details-image-ui"),
            ("ecom-details-image-plugin", "https://github.com/liangdabiao/ecom-details-image-plugin"),
        ],
        "style": "tech-dark",
        "covers": ["ecom-details-image-ui", "ecom-details-image-plugin"],
    },
    {
        "slug": "series-agent-stack",
        "title": "Agent 技术栈 · 四个切面",
        "repo": None,
        "repo_list": [
            ("Simple-Agentic-Stack", "https://github.com/liangdabiao/Simple-Agentic-Stack"),
            ("do-deepagents-skill", "https://github.com/liangdabiao/do-deepagents-skill"),
            ("langgraph-runtime-skill-agent", "https://github.com/liangdabiao/langgraph-runtime-skill-agent"),
        ],
        "style": "tech-dark",
        "covers": ["simple-agentic-stack", "do-deepagents-skill",
                   "langgraph-runtime-skill-agent"],
    },
    {
        "slug": "series-toolbox",
        "title": "AI 工具箱 · 两种打包",
        "repo": None,
        "repo_list": [
            ("simple_ai_toolset", "https://github.com/liangdabiao/simple_ai_toolset"),
            ("fetch-everything", "https://github.com/liangdabiao/fetch-everything"),
        ],
        "style": "tech-dark",
        "covers": ["simple-ai-toolset", "fetch-everything"],
    },
    # ── 2026-10-23 第七批（收尾）
    {
        "slug": "series-research",
        "title": "调研三件套 · 数据从哪来",
        "repo": None,
        "repo_list": [
            ("social_research_agent", "https://github.com/liangdabiao/social_research_agent"),
            ("Business_Idea_Validator", "https://github.com/liangdabiao/Business_Idea_Validator"),
            ("claude-data-analysis-ultra-main", "https://github.com/liangdabiao/claude-data-analysis-ultra-main"),
        ],
        "style": "study",
        "covers": ["social-research-agent", "business-idea-validator",
                   "claude-data-analysis-ultra-main"],
    },
    {
        "slug": "series-data-analysis",
        "title": "数据分析 · 两条路",
        "repo": None,
        "repo_list": [
            ("easy-amazon-voc", "https://github.com/liangdabiao/easy-amazon-voc"),
            ("HSTECH_2026_AI_SUMMARY", "https://github.com/liangdabiao/HSTECH_2026_AI_SUMMARY"),
        ],
        "style": "tech-dark",
        "covers": ["easy-amazon-voc", "hstech-2026-ai-summary"],
    },
    {
        "slug": "series-knowledge",
        "title": "知识库与学习",
        "repo": None,
        "repo_list": [
            ("llm-wiki", "https://github.com/liangdabiao/llm-wiki"),
            ("liangdabiao.github.io", "https://github.com/liangdabiao/liangdabiao.github.io"),
        ],
        "style": "chalkboard",
        "covers": ["llm-wiki", "liangdabiao-github-io"],
    },
    {
        "slug": "series-plugin-dev",
        "title": "扩展 AI · 两条路",
        "repo": None,
        "repo_list": [
            ("skill-ten-prompt-generator", "https://github.com/liangdabiao/skill-ten-prompt-generator"),
            ("dsh-plugin-developer-skill", "https://github.com/liangdabiao/dsh-plugin-developer-skill"),
        ],
        "style": "tech-dark",
        "covers": ["skill-ten-prompt-generator", "dsh-plugin-developer-skill"],
    },
    {
        "slug": "series-beads",
        "title": "拼豆 · 图纸的两端",
        "repo": None,
        "repo_list": [
            ("perler-beads-ai", "https://github.com/liangdabiao/perler-beads-ai"),
            ("perlerBeadsApplet", "https://github.com/liangdabiao/perlerBeadsApplet"),
        ],
        "style": "chalkboard",
        "covers": ["perler-beads-applet"],
    },
]

# md 文件名 → 它属于哪条系列片
SERIES_OF: dict[str, str] = {}
for _s in SERIES:
    for _m in _s["covers"]:
        SERIES_OF[_m] = _s["slug"]

# 风格建议：按关键词判。命中越靠前优先级越高。
# tech-dark 只看**标题**——否则几乎所有 AI 项目正文都提到 API/Agent，会被全判成深色。
STYLE_RULES = [
    ("chalkboard", ["数学", "证明", "公式", "几何", "推导", "勾股", "欧拉", "化学", "物理", "解题", "科普"]),
    ("warm-story", ["生意", "创业", "选品", "商业", "心理", "小生意", "赚钱", "市场调研", "销", "选品"]),
]
TECH_TITLE_KEYS = ["MCP", "API", "框架", "架构", "CLI", "RPA", "部署", "数据库", "RAG", "Agent",
                   "SDK", "LangGraph", "CrewAI", "爬虫", "抓取", "终端", "服务器", "数据"]


def suggest_style(stem: str, title: str, head: str) -> str:
    """按关键词给风格建议；拿不准就用 whiteboard（最百搭）。"""
    body = (head + " " + stem).lower()
    for style, keys in STYLE_RULES:
        if any(k.lower() in body for k in keys):
            return style
    if any(k.lower() in (title + " " + stem).lower() for k in TECH_TITLE_KEYS):
        return "tech-dark"
    return "whiteboard"


def repo_of(md_text: str, meta_link: str | None, stem: str = "") -> tuple[str | None, str | None]:
    """返回 (仓库地址, 来源说明)。优先级：md 行 > 人工确认表 > meta。"""
    m = re.search(r"代码仓库[：:]\s*(\S+)", md_text)
    if m:
        return m.group(1).rstrip("/"), "md"
    if stem in REPO_OVERRIDE:
        return REPO_OVERRIDE[stem][0], "confirmed"
    if meta_link:
        return meta_link.rstrip("/"), "meta"
    return None, None


def find_film(films: Path, stem: str, title: str, repo: str | None) -> Path | None:
    """在成片目录里找这个项目的片子。返回项目目录（含 out/*.mp4）或 None。"""
    cands: list[Path] = []
    if stem in ALIAS:
        cands.append(films / ALIAS[stem])
    cands.append(films / stem)
    # 仓库名 → 目录名（小写、下划线转连字符）
    if repo:
        slug = repo.rstrip("/").split("/")[-1] if "/tree/" not in repo else repo.split("/")[3]
        cands.append(films / slug.lower().replace("_", "-"))
    for c in cands:
        if c.is_dir() and list((c / "out").glob("*-有字幕.mp4")):
            return c
    # 兜底：扫所有项目，比对 script.js 里的 title
    if title:
        key = title.split("——")[0].strip()[:10]
        for c in films.glob("*/script.js"):
            try:
                s = c.read_text(encoding="utf-8")
            except OSError:
                continue
            if key and key in s and list((c.parent / "out").glob("*-有字幕.mp4")):
                return c.parent
    return None


def real_style(film: Path | None) -> str | None:
    """已完成的片子：直接读 script.js 的 META.style —— 比关键词猜准。"""
    if not film:
        return None
    sp = film / "script.js"
    if not sp.exists():
        return None
    try:
        m = re.search(r"style:\s*'([\w-]+)'", sp.read_text(encoding="utf-8"))
    except OSError:
        return None
    return m.group(1) if m else None


def main() -> int:
    ap = argparse.ArgumentParser(description="生成技能介绍视频进度表")
    ap.add_argument("--src", default=r"E:/all-skill-t0/skill-intros")
    ap.add_argument("--films", default=r"D:/films")
    ap.add_argument("--out", default=r"D:/films/PROGRESS.md")
    a = ap.parse_args()

    src, films = Path(a.src), Path(a.films)
    if not src.is_dir():
        print(f"✗ 素材目录不存在：{src}", file=sys.stderr)
        return 1

    # meta：slug → link（补 md 缺失的仓库地址）
    meta: dict[str, str] = {}
    mp = src / ".workbuddy_meta.json"
    if mp.exists():
        try:
            for x in json.loads(mp.read_text(encoding="utf-8")):
                if x.get("slug") and x.get("link"):
                    meta[x["slug"]] = x["link"]
        except (json.JSONDecodeError, OSError):
            pass

    rows = []
    # 系列片覆盖的 md：只统计一次（记在 series_rows 里），不再进单片
    series_rows = []
    for s in SERIES:
        d = films / s["slug"]
        mp4 = next(iter(sorted((d / "out").glob("*-有字幕.mp4"))), None) if (d / "out").is_dir() else None
        series_rows.append({
            "slug": s["slug"], "title": s["title"], "repo": s["repo"],
            "repo_list": s.get("repo_list"), "style": s["style"],
            "covers": s["covers"], "mp4": mp4,
        })
    done_series_covers = {m for sr in series_rows if sr["mp4"] for m in sr["covers"]}

    for md in sorted(src.glob("*.md")):
        stem = md.stem
        if stem in NOT_PROJECTS or stem in EXCLUDE:
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        title_m = re.search(r"^#\s+(.+)$", text, re.M)
        title = title_m.group(1).strip() if title_m else stem
        repo, src_of = repo_of(text, meta.get(stem), stem)
        style = suggest_style(stem, title, text[:400])
        film = find_film(films, stem, title, repo)
        # 属于系列片、且系列片已完成 → 这个 md 也算完成
        if stem in done_series_covers and not film:
            film = films / SERIES_OF[stem]
        rows.append({
            "stem": stem, "title": title, "repo": repo, "repo_src": src_of,
            "style": style, "size": md.stat().st_size, "film": film,
            "real_style": real_style(film),
            "series": SERIES_OF.get(stem),
        })

    done = [r for r in rows if r["film"]]
    todo = [r for r in rows if not r["film"]]
    # 待做里剔除已归入系列片的（它们不算独立产出单元）
    todo_flat = [r for r in todo if not r["series"]]
    no_repo = [r for r in rows if not r["repo"] and not r["series"]]
    subpath = [r for r in rows if r["repo"] and "/tree/" in r["repo"]]
    thin = [r for r in todo_flat if r["size"] < 1500]

    s_done = [sr for sr in series_rows if sr["mp4"]]
    s_todo = [sr for sr in series_rows if not sr["mp4"]]
    # 单片产出单元 = 不属于任何系列片的（做完的 + 待做的）
    flat_done = [r for r in done if not r["series"]]
    flat_todo = todo_flat
    units_total = len(flat_done) + len(flat_todo) + len(series_rows)
    units_done = len(flat_done) + len(s_done)

    L: list[str] = []
    w = L.append
    w("# 技能介绍视频 · 进度表")
    w("")
    w("> 由 `scripts/progress.py` 自动生成，**不要手改**。新增片子后重跑脚本即可更新。")
    w(f"> 素材：`{src}` · 成片：`{films}`")
    w("")
    w("## 总览")
    w("")
    w("**按产出单元算**（一条视频 = 1 个单元；系列片一条覆盖多个 md）")
    w("")
    w(f"| 指标 | 数量 |")
    w(f"|---|---|")
    w(f"| md 素材总数 | {len(rows)} |")
    w(f"| ✅ 已覆盖的 md | **{len(done)}** |")
    w(f"| 产出单元总数 | **{units_total}**（单片 {len(flat_done) + len(flat_todo)} + 系列 {len(series_rows)}） |")
    w(f"| ✅ 已完成单元 | **{units_done}**（单片 {len(flat_done)} + 系列 {len(s_done)}） |")
    w(f"| ⬜ 待做单元 | **{units_total - units_done}** |")
    w(f"| 完成率（按单元） | {units_done / max(1, units_total) * 100:.1f}% |")
    w(f"| 仓库地址缺失 | {len(no_repo)} |")
    w(f"| 素材偏薄（<1.5KB） | {len(thin)} |")
    w("")

    # ── 系列片
    w("## 🎬 系列片（N 个 md 合成一条）")
    w("")
    w("同一仓库的多个子技能、或同一套模板的多个变体，**合成一条讲共性与差异**。")
    w("分开做会高度重复，观众也记不住区别。")
    w("")
    w("| 状态 | 片名 | 风格 | 覆盖 | 仓库 |")
    w("|---|---|---|---|---|")
    for sr in series_rows:
        st = "✅" if sr["mp4"] else "⬜"
        repo = sr["repo"] or (f"{len(sr['repo_list'])} 个仓库" if sr["repo_list"] else "—")
        w(f"| {st} | `{sr['slug']}`<br>{sr['title']} | {sr['style']} | {len(sr['covers'])} 个 | {repo} |")
    w("")
    if s_todo:
        w("**待做系列片覆盖的 md**：")
        w("")
        for sr in s_todo:
            w(f"- `{sr['slug']}` ← {', '.join('`'+c+'`' for c in sr['covers'])}")
        w("")

    # 各风格分布（已做 vs 待做）
    w("### 风格分布")
    w("")
    w("| 风格 | 已做 | 待做 | 小计 |")
    w("|---|---|---|---|")
    for st in ["tech-dark", "whiteboard", "chalkboard", "warm-story", "study"]:
        d_n = sum(1 for r in done if (r["real_style"] or r["style"]) == st)
        t_n = sum(1 for r in todo if r["style"] == st)
        if d_n == 0 and t_n == 0:
            continue
        w(f"| {st} | {d_n} | {t_n} | {d_n + t_n} |")
    w("")

    # 下一批建议：素材最厚 + 仓库地址齐全 —— 厚的先做，内容才立得住
    ready = sorted([r for r in todo_flat if r["repo"]], key=lambda x: -x["size"])[:6]
    if ready:
        w("### 下一批建议（素材最厚、地址齐全）")
        w("")
        w("> 素材厚的先做：内容撑得起 8 页，不容易做成空壳。")
        w("")
        w("| # | md 文件 | 建议风格 | 大小 |")
        w("|---|---|---|---|")
        for i, r in enumerate(ready, 1):
            w(f"| {i} | `{r['stem']}.md` | {r['style']} | {r['size'] / 1024:.1f}KB |")
        w("")

    # ── 已完成
    w("## ✅ 已完成")
    w("")
    w("| # | 项目 | 风格 | 成片 |")
    w("|---|---|---|---|")
    for i, r in enumerate(done, 1):
        mp4 = next((r["film"] / "out").glob("*-有字幕.mp4"))
        size = mp4.stat().st_size / 1048576
        tag = f"（系列片 `{r['series']}`）" if r["series"] else ""
        w(f"| {i} | `{r['stem']}`{tag} | {r['real_style'] or r['style']} | [{mp4.name}]({mp4.as_posix()}) · {size:.1f}MB |")
    w("")

    # ── 待做：按风格分组，方便批量
    w("## ⬜ 待制作（单片，一个 md 一条）")
    w("")
    w("按**建议风格**分组 —— 同一批做同一风格，配音和画风都更容易保持一致。")
    w("")
    for style in ["tech-dark", "whiteboard", "chalkboard", "warm-story", "study"]:
        grp = [r for r in todo_flat if r["style"] == style]
        if not grp:
            continue
        w(f"### {style}（{len(grp)} 个）")
        w("")
        w("| # | md 文件 | 仓库 | 大小 | 备注 |")
        w("|---|---|---|---|---|")
        for i, r in enumerate(sorted(grp, key=lambda x: -x["size"]), 1):
            repo = r["repo"] or "**缺**"
            note = []
            if r["size"] < 1500:
                note.append("素材薄→可压 5 页")
            if r["repo"] and "/tree/" in r["repo"]:
                note.append("子路径")
            if not r["repo"]:
                note.append("需核实仓库")
            w(f"| {i} | `{r['stem']}.md` | {repo} | {r['size'] / 1024:.1f}KB | {'·'.join(note) or '—'} |")
        w("")

    # ── 需要人工确认
    if no_repo or subpath:
        w("## ⚠ 需要先处理")
        w("")
        if no_repo:
            w(f"**仓库地址缺失（{len(no_repo)} 个）** —— 地址页不能编，先核实：")
            w("")
            for r in no_repo:
                w(f"- `{r['stem']}.md`")
            w("")
        if subpath:
            w(f"**仓库是子路径（{len(subpath)} 个）** —— 地址页要同时显示父仓库 + 子路径，别只显示最后一段：")
            w("")
            for r in subpath:
                w(f"- `{r['stem']}` → `{r['repo']}`")
            w("")

    w("## 制作流程")
    w("")
    w("每条都走同一套（详见 `references/github-project-intro.md`）：")
    w("")
    w("```")
    w("① 读 md（1 次 Read）")
    w("② 写 script.js（8 页 × 3 句 = 21 条 cue）")
    w("③ ftvoice.py 后台配音 ← 期间并行写 8 页画面")
    w("④ ftcheck.py 1 轮，只修 error")
    w("⑤ 定点复查 --only pNN --no-sheets")
    w("⑥ ftrender.py --fps 24 后台渲染")
    w("```")
    w("")
    w("**纪律**：一条一个命令（配音/渲染都不许 `for` 循环）；lint 0 error 就渲染；")
    w("最后一页必须是仓库地址页。")
    w("")
    w("## 怎么更新这张表")
    w("")
    w("```bash")
    w("python scripts/progress.py              # 重新扫素材 + 成片，覆盖本文件")
    w("```")
    w("")
    w("**不要手改本文件**：状态是从「成片目录里有没有 `out/*-有字幕.mp4`」推出来的，")
    w("手工改会和事实不一致。新片渲染完，重跑一次脚本就自动变 ✅。")
    w("")
    w("如果某个项目的成片目录名和 md 文件名差太远（自动匹配失败），")
    w("在 `scripts/progress.py` 的 `ALIAS` 里加一行即可。")
    w("")

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")

    print(f"✓ 进度表 → {out}")
    print(f"  md {len(rows)} · 已覆盖 {len(done)} · 产出单元 {units_total}（完成 {units_done} / 待做 {units_total - units_done}）")
    print(f"  系列片 {len(series_rows)} 条（完成 {len(s_done)}）覆盖 {sum(len(s['covers']) for s in SERIES)} 个 md")
    if no_repo:
        print(f"  ⚠ 缺仓库地址 {len(no_repo)} 个")
    if subpath:
        print(f"  ⚠ 子路径仓库 {len(subpath)} 个")
    return 0


if __name__ == "__main__":
    sys.exit(main())
