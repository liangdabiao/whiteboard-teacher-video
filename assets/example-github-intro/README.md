# 参考实现：GitHub 项目介绍视频（8 页 · 白板风）

一条**真实成片**的完整源码。主题恰好是介绍本 skill 自己（`whiteboard-explainer`），
所以你可以同时看到「怎么讲一个项目」和「怎么画出来」。

配套方法论：`references/github-project-intro.md`

## 结构（这就是标准骨架）

| 页 | 内容 | 手法 |
|---|---|---|
| p01 | 不是 PPT 翻页 | 左右对比：一叠整页翻过的幻灯片 vs 正在一笔笔画的圆 |
| p02 | 图形一笔笔描 | 房子分三笔（屋顶 / 墙 / 门），第三笔换蓝笔 |
| p03 | 讲到哪画到哪 | 旁白时间轴 + `P.cw` 让「月亮」念到那一刻才画 |
| p04 | 两种模式 | 左右分屏：逐拍幻灯片 vs 单画布长满 |
| p05 | 本地 CPU 零成本 | 云端打红叉 vs 本机 CPU 打勾 |
| p06 | 全链路免费 | 四段流水线：PIL / Agnes / edge-tts / ffmpeg |
| p07 | 适合谁 | 三张场景卡 + 收尾落在延伸的箭头上 |
| **p08** | **仓库地址页** | **仓库名大字 + 完整 URL + 「怎么找到」← 每条项目介绍片必须有** |

## 文件

```
script.js         META + 8 页 × 3 句 = 21 条 cue（gap 0.5）
pages/p01–p08.js  每页一个 ENGINE.visual
```

产物（`audio/` `voice.js` `out/`）不在这里——它们是生成出来的，不要入库。

## 怎么用

```bash
# 1. 复制骨架（含 engine 链接的做法不同，见下）
cp -r assets/example-github-intro D:/films/我的新项目

# 2. 用 ftnew 补 engine 链接（幂等，不会覆盖已有 script.js）
python scripts/ftnew.py D:/films/我的新项目 --title "项目名" --style whiteboard

# 3. 改 script.js 的口播，再改各页画面
# 4. 配音 → 质检 → 渲染
python scripts/ftvoice.py D:/films/我的新项目 --backend edge --voice mature --speed 1.15
python scripts/ftcheck.py D:/films/我的新项目
python scripts/ftrender.py D:/films/我的新项目 --fps 24
```

## 抄什么、不抄什么

**抄**：页数节奏、每页只讲一个观点、cue 的切分方式、地址页的四件套、箭头/落位的时序
（`t1 + i * 0.45`）。

**不抄**：具体图形、配色分配、比喻物体。每个项目要按它自己的内容选视觉——
讲数据管道就用管道，讲验证就用秤，讲证明就用几何图形。
照抄形状会让所有片子长得一样，观众看不出差别。
