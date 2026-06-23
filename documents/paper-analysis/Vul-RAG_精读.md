# 精读笔记：Vul-RAG — Enhancing LLM-based Vulnerability Detection via Knowledge-level RAG

## A. 大白话总结（3-5 句）

这篇论文先做了一个"揭底"实验：发现 LLM（GPT-4o、Claude 等）区分漏洞代码和修补后代码的能力极差（pair accuracy 仅 0.06–0.14），基本等于随机猜。而且各种高级提示词（CoT、CWE 增强）也只带来 0.05–0.20 的提升。作者于是提出了 Vul-RAG：从历史 CVE 中提取多维度漏洞知识（功能语义、漏洞原因、修复方案），检测时检索相关知识辅助 LLM 判断。最终 pair accuracy 提升 16%–24%，还在 Linux 内核 v6.9.6 中发现了 10 个此前未知的 bug，其中 6 个已分配 CVE。

## B. 术语卡片

1. **PairVul 基准**：586 对高质量漏洞/修复代码对（来自 Linux 内核 CVE），专门测试 LLM 区分相似代码的能力。
2. **知识级 RAG（Knowledge-level RAG）**：不同于传统代码级 RAG（直接检索代码片段），Vul-RAG 检索的是高层语义知识（漏洞原因、修复方案），避免 LLM 被表面词法特征误导。
3. **Unstable Bias**：LLM 在不同中性提示词下表现出不稳定的偏向——有的提示词让 LLM 倾向于把所有代码判为有漏洞，有的则倾向于全判为无漏洞。
4. **多维度知识表示**：功能语义（抽象目的+详细行为）、漏洞原因（触发操作+抽象描述+详细描述）、修复方案。共 7 个元素。

## C. 核心知识点（硬数字）

| 发现 | 数据 |
|------|------|
| PairVul 基准 | 586 对代码，420 个 CVE，Top-10 CWE |
| LLM 基础 Pair Accuracy | 0.06–0.14（86%–94% 案例区分失败） |
| 高级提示词最佳效果 | CoT-1 + GPT-4o 仅 0.20 pair accuracy |
| Vul-RAG 提升 | pair accuracy ↑16%–24%，平衡精确率 ↑9%–14%，平衡召回率 ↑7%–11% |
| 对比代码级 RAG | 高出 16%–27% pair accuracy |
| 对比微调基线 | 高出 22%–26% pair accuracy |
| 人工检测辅助 | 准确率从 60% → 77%（使用 Vul-RAG 知识后） |
| 真实漏洞发现 | Linux v6.9.6 中发现 10 个新 bug，6 个已分配 CVE |
| 不稳定偏向 | GPT-4o 在 basic prompt 下判 77% 为有漏洞，CoT-1 下仅判 48% |
