#!/bin/bash
# 并行下载全部49篇综述论文 PDF
# arXiv 论文直接抓，DOI-only 论文尝试后记入 missing.txt
set -e

BASE="/home/xx/项目/.trae/papers"
JOBS=8                                  # 并发数
MISSING="${BASE}/missing.txt"
TASKLIST=$(mktemp)
trap "rm -f $TASKLIST" EXIT

echo "=========================================="
echo "综述论文并行下载（49 篇，${JOBS} 并发）"
echo "=========================================="

# ---- 单个下载函数（xargs 调用）----
download_one() {
    local id="$1" out="$2" label="$3" retries=2
    local url
    case "$id" in
        DOI:*) url="https://doi.org/${id#DOI:}" ;;
        *)     url="https://arxiv.org/pdf/${id}" ;;
    esac

    # 跳过已存在的完整 PDF
    if [ -f "$out" ] && [ "$(stat -c%s "$out" 2>/dev/null || echo 0)" -gt 5000 ]; then
        echo "[OK] $label (已有)"
        return 0
    fi

    for i in $(seq 1 $retries); do
        if curl -fSL --connect-timeout 15 --max-time 120 -o "$out" "$url" 2>/dev/null; then
            local sz=$(stat -c%s "$out" 2>/dev/null || echo 0)
            if [ "$sz" -gt 5000 ]; then
                echo "[OK] $label ($(du -h "$out" | cut -f1))"
                return 0
            fi
        fi
        [ $i -lt $retries ] && sleep 2
    done

    # 失败
    echo "[XX] $label" >&2
    echo "$label  |  $id  |  $url" >> "$MISSING"
    rm -f "$out"
    return 1
}

export -f download_one
export MISSING

# ---- 任务清单 ----
> "$MISSING"  # 清空

add_task() { echo "$1|$2|$3" >> "$TASKLIST"; }
# 参数: arXiv_ID或DOI:xxx | 输出路径 | 标签

# 方向① — LLM漏洞检测综述 (3)
D1="${BASE}/direction-01-survey"
add_task "2502.07049"  "${D1}/sheng2025-LLMs-Software-Security-Survey.pdf"          "sheng:2025"
add_task "2412.15004"  "${D1}/basic2024-Vulnerabilities-to-Remediation.pdf"          "basic:2024"
add_task "2502.18474"  "${D1}/wang2025-LLM-Program-Analysis-Survey.pdf"              "wang:2025"

# 方向② — SCA/版本/可达 (9)
D2="${BASE}/direction-02-sca"
add_task "2506.18050"  "${D2}/zhang2025-VFArche.pdf"                  "VFArche★"
add_task "2408.07321"  "${D2}/cheng2024-VERCATION.pdf"               "VERCATION★"
add_task "1909.00973"  "${D2}/foo2019-SCA-Dynamics.pdf"              "Dynamics"
add_task "2409.06816"  "${D2}/yu2024-Patch-Localization.pdf"         "PatchLoc"
add_task "2412.20740"  "${D2}/tan2025-Similar-but-Patched.pdf"       "SimilarPatched"
add_task "DOI:10.1109/ICSE43902.2022.9794006" "${D2}/bao2022-V-SZZ.pdf" "V-SZZ(DOI)"
add_task "2506.17798"  "${D2}/lingxiang2025-SAVANT.pdf"              "SAVANT◆"
add_task "2503.22576"  "${D2}/zhang2025-DGA.pdf"                     "DGA"
add_task "2507.18957"  "${D2}/chang2025-SLICEMATE.pdf"               "SLICEMATE"

# 方向③ — LLM消减误报 (11)
D3="${BASE}/direction-03-fp-reduction"
add_task "2506.16899"  "${D3}/wagner2025-Complementary-Security.pdf"      "保守分析★"
add_task "2510.02534"  "${D3}/iranmanesh2025-ZeroFalse.pdf"               "ZeroFalse"
add_task "2506.10322"  "${D3}/du2025-LLM4PFA.pdf"                         "LLM4PFA"
add_task "2411.03079"  "${D3}/chen2024-LLM4FPM.pdf"                       "LLM4FPM"
add_task "2601.22952"  "${D3}/xiong2026-Sifting-the-Noise.pdf"            "Sifting★"
add_task "DOI:10.1145/3653718" "${D3}/wen2024-LLM4SA.pdf"                 "LLM4SA(DOI)"
add_task "2511.04023"  "${D3}/lin2025-AdaTaint.pdf"                       "AdaTaint"
add_task "2509.11787"  "${D3}/joos2025-CodeCureAgent.pdf"                 "CodeCureAgent"
add_task "2509.15433"  "${D3}/agrawal2025-SAST-Genius.pdf"                "SAST-Genius"
add_task "2605.01885"  "${D3}/ameen2026-QASecClaw.pdf"                    "QASecClaw"
add_task "2509.16275"  "${D3}/gajjar2025-SecureFixAgent.pdf"              "SecureFixAgent◆"

# 方向④ — LLM+图/CodeQL (11)
D4="${BASE}/direction-04-llm-graph"
add_task "2405.17238"  "${D4}/li2024-IRIS.pdf"                             "IRIS★"
add_task "2507.16585"  "${D4}/lekssays2025-LLMxCPG.pdf"                    "LLMxCPG"
add_task "2503.09089"  "${D4}/chen2025-LocAgent.pdf"                       "LocAgent"
add_task "2509.22530"  "${D4}/cheng2025-Boosting-Pointer-Analysis.pdf"     "BoostingPA"
add_task "2402.10754"  "${D4}/wang2024-LLMDFA.pdf"                         "LLMDFA"
add_task "DOI:10.1016/j.jss.2024.112031" "${D4}/lu2024-GRACE.pdf"          "GRACE(DOI)"
add_task "2601.10865"  "${D4}/ghebremichael2026-SemTaint.pdf"              "SemTaint◆"
add_task "2404.14719"  "${D4}/liu2024-Vul-LMGNNs.pdf"                      "Vul-LMGNNs"
add_task "2509.11523"  "${D4}/wang2025-VulAgent.pdf"                       "VulAgent"
add_task "2510.15112"  "${D4}/khatun2025-AndroByte.pdf"                    "AndroByte"
add_task "2510.10321"  "${D4}/gajjar2025-Bridging.pdf"                     "Bridging◆"

# 方向⑤ — 智能体/定位/复现 (6)
D5="${BASE}/direction-05-agent"
add_task "2510.02389"  "${D5}/xi2025-T2L-Agent.pdf"       "T2L-Agent"
add_task "2509.01835"  "${D5}/ullah2025-CVE-Genie.pdf"    "CVE-Genie"
add_task "2605.21392"  "${D5}/sun2026-VIPER-MCP.pdf"      "VIPER-MCP"
add_task "2606.03453"  "${D5}/shaikh2026-FORGE.pdf"       "FORGE"
add_task "2604.10800"  "${D5}/gajjar2026-Verify-Before-Fix.pdf" "Verify"
add_task "2604.20179"  "${D5}/ni2026-LLMVD-js.pdf"        "LLMVD.js"

# 方向⑥ — 数据集/评测 (7)
D6="${BASE}/direction-06-benchmark"
add_task "2411.17274"  "${D6}/li2024-CleanVul.pdf"        "CleanVul"
add_task "2304.00409"  "${D6}/chen2023-DiverseVul.pdf"    "DiverseVul"
add_task "2301.05456"  "${D6}/croft2023-Data-Quality.pdf" "Croft"
add_task "2404.00287"  "${D6}/zhang2024-Eval-Line-Level.pdf" "Eval"
add_task "2603.10969"  "${D6}/damie2026-TOSSS.pdf"        "TOSSS"
add_task "2601.22706"  "${D6}/wang2026-RealSec-bench.pdf" "RealSec-bench"
add_task "2601.19239"  "${D6}/li2026-ProjectScale.pdf"    "ProjectScale"

# 早期 2022–2023 (9)
DE="${BASE}/early-2022-2023"
add_task "2112.02125"  "${DE}/pearce2021-ZeroShot-Vuln-Repair.pdf"  "Pearce"
add_task "2310.09810"  "${DE}/fu2023-ChatGPT-How-Far.pdf"           "Fu-ChatGPT"
add_task "2311.12420"  "${DE}/gao2023-How-Far-Vuln-Detection.pdf"  "Gao"
add_task "2312.12575"  "${DE}/ullah2023-LLMs-Cannot-Reliably.pdf"   "Ullah"
add_task "2308.12697"  "${DE}/zhang2023-Prompt-Enhanced-Vuln.pdf"   "Zhang-prompt"
add_task "2306.01754"  "${DE}/chan2023-EditTime.pdf"                "Chan"
add_task "2202.13169"  "${DE}/xu2022-Code-LLM-Eval.pdf"             "Xu"
add_task "2301.08653"  "${DE}/sobania2023-ChatGPT-Bug-Fixing.pdf"   "Sobania"
add_task "DOI:10.1145/3524842.3528452" "${DE}/fu2022-LineVul.pdf"   "LineVul(DOI)"

TOTAL=$(wc -l < "$TASKLIST")
echo "任务数: $TOTAL"
echo "开始并行下载..."
echo ""

# ---- 执行 ----
# xargs 0 表示用 NUL 分隔，但这里用换行分隔更简单
# 将 tasklist 转为可执行的命令
cat "$TASKLIST" | xargs -P "$JOBS" -I {} bash -c '
    IFS="|" read -r id out label <<< "{}"
    download_one "$id" "$out" "$label"
'

echo ""
echo "=========================================="
echo "下载完成。统计："
echo "=========================================="

SUCCESS=0
for d in "$BASE"/*/; do
    dirname=$(basename "$d")
    count=$(find "$d" -maxdepth 1 -name "*.pdf" -type f 2>/dev/null | wc -l)
    size=$(du -sh "$d" 2>/dev/null | cut -f1)
    printf "  %-30s %2d 篇 (%s)\n" "$dirname" "$count" "$size"
    SUCCESS=$((SUCCESS + count))
done

echo "  ------------------------------"
echo "  成功: $SUCCESS / $TOTAL"

FAILED=$((TOTAL - SUCCESS))
echo ""
if [ "$FAILED" -gt 0 ]; then
    echo "缺失 $FAILED 篇（见 $MISSING）："
    cat "$MISSING"
else
    echo "全部下载成功！"
fi

chown -R xx:xx "$BASE" 2>/dev/null || true
echo ""
echo "权限已修正为 xx:xx"
