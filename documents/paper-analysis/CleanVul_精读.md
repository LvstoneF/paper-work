# 精读笔记：CleanVul — Toward High-Quality Function-Level Vulnerability Datasets via LLM-Based Noise Reduction

## A. 大白话总结（3-5 句）

现有漏洞数据集噪音极大（40%-75% 的标签是错的），因为 VFC（修复漏洞的提交）里经常掺杂了测试改进、重构、文档更新等无关改动。CleanVul 提出了 VulSifter——用 LLM + 启发式规则自动从 VFC 中筛选出真正与漏洞相关的函数改动，GPT-4 F1 达 0.82。最终产出 CleanVul 数据集（8,198 个函数），正确率 90.6%，达到人工校验水平。实验证明在 CleanVul 上训练的模型泛化能力更强，甚至跨数据集测试时优于在 PrimeVul 上训练的模型。

## B. 术语卡片

1. **VFC（Vulnerability-Fixing Commit）**：标记为修复漏洞的 Git 提交，但其中可能混杂非漏洞相关的改动（"纠结提交"）。
2. **VulSifter**：组合 LLM 语义理解 + 启发式过滤的两阶段方法，自动识别 VFC 中的真实漏洞修复改动。
3. **纠结提交（Tangled Commit）**：一个提交同时包含漏洞修复和其他无关改动（如重构、测试、文档），是数据集噪音的主要来源。
4. **Correctness 指标**：数据集中真正漏洞函数的占比（而非传统 P/R/F1），CleanVul 达 90.6%（PrimeVul 86%、SVEN 94%）。

## C. 核心知识点（硬数字）

| 发现 | 数据 |
|------|------|
| 现有数据噪音率 | 40%–75%（自动标注导致） |
| 噪音分类 | 测试相关 41.2%、普通 bug 修复 38.2%、重构/文档 20.6% |
| VulSifter（GPT-4）F1 | 0.82 |
| CleanVul 正确率 | 90.6%（PrimeVul 86%、SVEN 94%） |
| 数据集规模 | 8,198 个函数（vuln + benign 平衡） |
| 抓取源 | 127,063 个 GitHub 仓库、5,352,105 个 commit |
| CleanVul 训练→PrimeVul 测试 | 58.09%（> PrimeVul 自测 56.61%） |
| CleanVul 训练→SVEN 测试 | 64.87%（> PrimeVul→SVEN 55.75%） |
| 覆盖语言 | Java、Python、JavaScript、C#、C、C++ |
| 非 NVD 依赖 | 不依赖 NVD 条目，适用性更广 |
