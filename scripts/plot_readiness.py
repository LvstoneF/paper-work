#!/usr/bin/env python3
"""部署就绪度热力图：每篇论文在 4 个就绪度维度上的评分

用法:
    python3 scripts/plot_readiness.py [--output readiness.png]
"""

import argparse
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# 配置 CJK 字体
_cjk_fonts = [f for f in fm.findSystemFonts() if "Noto" in f and ("CJK" in f or "Sans" in f)]
if _cjk_fonts:
    _prop = fm.FontProperties(fname=_cjk_fonts[0])
    plt.rcParams["font.family"] = _prop.get_name()
else:
    plt.rcParams["font.family"] = "sans-serif"

# ── 就绪度维度 ─────────────────────────────────────
READINESS_DIMS = [
    "可编译性要求\n(越低越好)",
    "云端大模型依赖\n(越低越好)",
    "可解释性\n(越高越好)",
    "真实代码库验证\n(越高越好)",
]

# 子方向颜色 (与 plot_matrix 一致)
DIRECTION_COLORS = {
    "①": "#e41a1c",
    "②": "#377eb8",
    "③": "#4daf4a",
    "④": "#984ea3",
    "⑤": "#ff7f00",
    "⑥": "#a65628",
    "早期": "#999999",
}


def parse_direction(label: str) -> str:
    for d in ["①", "②", "③", "④", "⑤", "⑥"]:
        if d in label:
            return d
    return "早期"


def parse_readiness(row: dict) -> list[float]:
    """解析 4 个就绪度维度,返回 [0-1] 评分."""
    scores = []

    # 就绪度-可编译性: "是"(需编译)=0, "否"(不需编译)=1
    val = row.get("就绪度-可编译性", "").strip()
    if val == "是":
        scores.append(0.0)
    elif val == "否":
        scores.append(1.0)
    else:
        scores.append(0.5)  # 未知

    # 就绪度-云端依赖: "是"(依赖云端)=0, "否"(可离线)=1
    val = row.get("就绪度-云端依赖", "").strip()
    if val in ("是", "依赖"):
        scores.append(0.0)
    elif val in ("否", "可离线"):
        scores.append(1.0)
    else:
        scores.append(0.5)

    # 就绪度-可解释性: "是"/"部分"→ 1/0.5
    val = row.get("就绪度-可解释性", "").strip()
    if val in ("是", "高"):
        scores.append(1.0)
    elif val in ("部分", "中"):
        scores.append(0.5)
    else:
        scores.append(0.25)

    # 就绪度-真实代码库: "是"→ 1, 其他→ 0
    val = row.get("就绪度-真实代码库", "").strip()
    if val == "是":
        scores.append(1.0)
    elif val == "部分":
        scores.append(0.5)
    else:
        scores.append(0.25)

    return scores


def plot_readiness(csv_path: str, output_path: str):
    """绘制部署就绪度热力图."""
    papers = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("简称", "?")
            direction = parse_direction(row.get("子方向", ""))
            scores = parse_readiness(row)
            if all(s == 0.5 or s == 0.25 for s in scores):
                continue  # 纯未知数据跳过
            papers.append({
                "name": name,
                "direction": direction,
                "scores": scores,
            })

    if not papers:
        print("无有效数据点,无法绘图")
        return

    print(f"有效数据点: {len(papers)}")

    # 按方向分组排序
    papers.sort(key=lambda p: (p["direction"], p["name"]))

    # ── 绘图 ──────────────────────────────────────
    n_papers = len(papers)
    fig_height = max(6, n_papers * 0.38)
    fig, ax = plt.subplots(figsize=(12, fig_height))

    data_matrix = np.array([p["scores"] for p in papers])
    names = [p["name"] for p in papers]
    dir_colors = [DIRECTION_COLORS.get(p["direction"], "#333333") for p in papers]

    # 热力图
    im = ax.imshow(data_matrix, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)

    # 标注数值
    for i in range(n_papers):
        for j in range(len(READINESS_DIMS)):
            val = data_matrix[i, j]
            text_color = "white" if val < 0.4 or val > 0.6 else "black"
            label = {0.0: "✗", 1.0: "✓", 0.5: "?", 0.25: "?"}.get(val, "?")
            ax.text(j, i, label, ha="center", va="center",
                   fontsize=9, fontweight="bold", color=text_color)

    # 纵轴标签 + 方向颜色条
    ax.set_yticks(range(n_papers))
    ax.set_yticklabels(names, fontsize=9)
    for i, c in enumerate(dir_colors):
        ax.get_yticklabels()[i].set_color(c)

    ax.set_xticks(range(len(READINESS_DIMS)))
    ax.set_xticklabels(READINESS_DIMS, fontsize=10)
    ax.set_title(f"部署就绪度热力图 ({n_papers} 篇论文)\n"
                 "✓=满足  ?=未知/部分  ✗=不满足",
                 fontsize=13, fontweight="bold")

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label("就绪度评分 (0=低 → 1=高)", fontsize=9)

    # 图例
    from matplotlib.patches import Patch
    legend_patches = [Patch(color=c, label=d)
                      for d, c in sorted(DIRECTION_COLORS.items())
                      if d in set(p["direction"] for p in papers)]
    ax.legend(handles=legend_patches, fontsize=8, loc="lower right",
              bbox_to_anchor=(1.05, -0.02), framealpha=0.9, ncol=3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"就绪度热力图已保存: {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="绘制部署就绪度热力图")
    parser.add_argument("--csv", default="papers.csv", help="papers.csv 路径")
    parser.add_argument("--output", "-o", default="documents/部署就绪度热力图.png",
                        help="输出图片路径")
    args = parser.parse_args()

    plot_readiness(args.csv, args.output)


if __name__ == "__main__":
    main()
