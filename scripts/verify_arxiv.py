#!/usr/bin/env python3
"""验证 CLAUDE.md 中所有 arXiv ID 可解析,输出核对报告。

用法:
    python3 scripts/verify_arxiv.py [--output report.md]
"""

import argparse
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# ── arXiv ID 来源 ──────────────────────────────────────────
# 从 CLAUDE.md 提取;格式: {方向: [(简称, arXiv ID), ...]}
# 加上"待核实区"论文

VERIFIED_PAPERS: dict[str, list[tuple[str, str]]] = {
    "① 综述": [
        ("sheng2025", "2502.07049"),
        ("basic2024", "2412.15004"),
        ("wang2025", "2502.18474"),
        ("du2025-VulRAG", "2406.11147"),
        ("yang2024-MSIVD", "2406.05892"),
        ("widyasari2024-BeyondChatGPT", "2409.01001"),
        ("wei2024-LLMSmartAudit", "2410.09381"),
    ],
    "② SCA/可达/版本": [
        ("VFArche", "2506.18050"),
        ("Vercation", "2408.07321"),
        ("Veracode-Dynamics", "1909.00973"),
        ("Patch-Localization", "2409.06816"),
        ("Similar-but-Patched", "2412.20740"),
    ],
    "③ LLM消减误报": [
        ("保守分析", "2506.16899"),
        ("ZeroFalse", "2510.02534"),
        ("LLM4PFA", "2506.10322"),
        ("LLM4FPM", "2411.03079"),
        ("Sifting-the-Noise", "2601.22952"),
    ],
    "④ LLM+图/CodeQL": [
        ("IRIS", "2405.17238"),
        ("LLMxCPG", "2507.16585"),
        ("LocAgent", "2503.09089"),
        ("Boosting-Pointer-Analysis", "2509.22530"),
    ],
    "⑤ 智能体/定位": [
        ("T2L-Agent", "2510.02389"),
        ("CVE-Genie", "2509.01835"),
    ],
    "⑥ 评测/数据集": [
        ("CleanVul", "2411.17274"),
        ("DiverseVul", "2304.00409"),
        ("Eval-行级定位", "2404.00287"),
    ],
    "早期 2022-2023": [
        ("Pearce", "2112.02125"),
        ("Fu-ChatGPT", "2310.09810"),
        ("Gao-How-Far", "2311.12420"),
        ("Ullah-Cannot-Reliably", "2312.12575"),
        ("Zhang-Prompt-Enhanced", "2308.12697"),
        ("Chan-EditTime", "2306.01754"),
        ("Xu-Code-LLM-Eval", "2202.13169"),
        ("Sobania-ChatGPT-Bug-Fixing", "2301.08653"),
    ],
}

# DOI-only papers (no arXiv ID)
DOI_ONLY: list[tuple[str, str, str]] = [
    ("Croft-DataQuality", "10.1109/ICSE48619.2023.00022", "⑥"),
    ("V-SZZ", "10.1109/ICSE43902.2022.9794006", "② 待核实"),
    ("LLM4SA", "10.1145/3653718", "③ 待核实"),
    ("GRACE", "10.1016/j.jss.2024.112031", "④ 待核实"),
    ("LineVul", "10.1145/3524842.3528452", "早期 待核实"),
]

# arXiv API endpoint
API = "https://export.arxiv.org/api/query?id_list={}&max_results=1"


def fetch_arxiv_metadata(arxiv_id: str, timeout: int = 30) -> dict | None:
    """从 arXiv API 获取论文元数据。"""
    url = API.format(arxiv_id)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ReviewVerify/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            xml_text = resp.read().decode("utf-8")
    except Exception as e:
        return {"error": str(e)}

    # arXiv API 返回的 XML 有命名空间
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    try:
        root = ET.fromstring(xml_text)
        entry = root.find("atom:entry", ns)
        if entry is None:
            return {"error": "No entry found in API response"}

        title = entry.find("atom:title", ns)
        title_text = title.text.strip().replace("\n", " ") if title is not None else "N/A"

        authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]

        published = entry.find("atom:published", ns)
        year = published.text[:4] if published is not None else "N/A"

        summary = entry.find("atom:summary", ns)
        summary_text = summary.text.strip()[:200] if summary is not None else "N/A"

        cat = entry.find("arxiv:primary_category", ns)
        category = cat.get("term") if cat is not None else "N/A"

        return {
            "title": title_text,
            "authors": authors,
            "year": year,
            "category": category,
            "summary": summary_text,
        }
    except ET.ParseError as e:
        return {"error": f"XML parse error: {e}"}


def verify_all(verbose: bool = True) -> dict:
    """验证所有 arXiv ID,返回结果字典。"""
    results: dict[str, list[dict]] = {}

    for direction, papers in VERIFIED_PAPERS.items():
        results[direction] = []
        for name, arxiv_id in papers:
            if verbose:
                print(f"  核对 {name} ({arxiv_id})...", end=" ", flush=True)
            meta = fetch_arxiv_metadata(arxiv_id)
            entry = {
                "name": name,
                "arxiv_id": arxiv_id,
                "status": "OK" if meta and "error" not in meta else "FAIL",
                "meta": meta,
            }
            results[direction].append(entry)
            if verbose:
                if entry["status"] == "OK":
                    print(f"✓ {meta['year']} — {meta['title'][:80]}")
                else:
                    print(f"✗ {meta.get('error', 'unknown')}")
            time.sleep(1.0)  # arXiv API rate limit 友好 (保守,避免 429)

    return results


def generate_report(results: dict, output_path: str | None = None) -> str:
    """生成 Markdown 核对报告。"""
    lines = [
        "# arXiv ID 核对报告",
        "",
        f"> 自动生成,核对 {sum(len(v) for v in results.values())} 篇论文",
        "",
        "## 摘要",
        "",
    ]

    total = sum(len(v) for v in results.values())
    ok_count = sum(1 for v in results.values() for e in v if e["status"] == "OK")
    fail_count = total - ok_count
    lines.append(f"- ✅ 可解析: {ok_count}/{total}")
    lines.append(f"- ❌ 不可解析: {fail_count}/{total}")
    lines.append("")

    for direction, entries in results.items():
        lines.append(f"## {direction}")
        lines.append("")
        for e in entries:
            status = "✅" if e["status"] == "OK" else "❌"
            meta = e["meta"]
            if e["status"] == "OK":
                authors_short = meta["authors"][0] if meta["authors"] else "N/A"
                lines.append(
                    f"- {status} **{e['name']}** `{e['arxiv_id']}` — "
                    f"{meta['year']} | {meta['category']} | {authors_short} | "
                    f"*{meta['title'][:100]}*"
                )
            else:
                lines.append(
                    f"- {status} **{e['name']}** `{e['arxiv_id']}` — "
                    f"错误: {meta.get('error', 'unknown')}"
                )
        lines.append("")

    # DOI-only section
    lines.append("## DOI-only / 待核实区")
    lines.append("")
    lines.append("以下论文仅有 DOI,无 arXiv ID,需手动到 dblp/出版商网站核实:")
    lines.append("")
    for name, doi, direction in DOI_ONLY:
        lines.append(f"- ⬜ **{name}** ({direction}) — DOI: `{doi}` — <https://doi.org/{doi}>")
    lines.append("")

    lines.append("---")
    lines.append(f"报告生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    report = "\n".join(lines)

    if output_path:
        Path(output_path).write_text(report, encoding="utf-8")
        print(f"\n报告已写入: {output_path}")

    return report


def main():
    parser = argparse.ArgumentParser(description="验证 arXiv ID 可解析性")
    parser.add_argument("--output", "-o", default="documents/arxiv-verify-report.md",
                        help="输出报告路径 (默认: documents/arxiv-verify-report.md)")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="静默模式,只输出报告不逐条打印")
    args = parser.parse_args()

    print(f"开始核对 {sum(len(v) for v in VERIFIED_PAPERS.values())} 个 arXiv ID...\n")
    results = verify_all(verbose=not args.quiet)

    print()
    generate_report(results, output_path=args.output)

    # 统计
    total = sum(len(v) for v in results.values())
    ok = sum(1 for v in results.values() for e in v if e["status"] == "OK")
    fail = total - ok
    print(f"完成: {ok} OK, {fail} FAIL, {len(DOI_ONLY)} DOI-only 待手动核实")

    return 1 if fail > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
