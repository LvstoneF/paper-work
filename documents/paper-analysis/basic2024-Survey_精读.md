# 精读笔记：From Vulnerabilities to Remediation — A Systematic Literature Review of LLMs in Code Security

## A. 大白话总结（3-5 句）

这是一篇聚焦"LLM 与代码安全"三个维度的系统性文献综述（SLR）：LLM 生成了什么漏洞、LLM 检测和修复漏洞的能力如何、数据投毒对 LLM 安全能力的影响。共纳入 102 篇论文，覆盖 2021–2026 年初。核心发现：LLM 生成的代码最常出现注入类漏洞（SQL/XSS），检测能力虽常超越传统 SAST 但误报率偏高（可达 63-97%），修复能力仅对简单/局部问题有效。本文独有贡献是将漏洞分类为 10 类、覆盖数据投毒影响、且同时审视了检测与修复的统一流程。

## B. 术语卡片

1. **SLR（Systematic Literature Review）**：系统性文献综述，遵循结构化方法（规划→执行→报告），有明确的研究问题、检索策略和筛选标准。
2. **Data Poisoning**：数据投毒攻击，攻击者在训练数据中注入恶意样本，使模型在特定条件下产生不安全输出。
3. **Self-repair Blind Spot**：LLM 能修复其他模型的不安全代码（60%），但对自己生成的代码修复效果很差——一种"自我修复盲区"。
4. **ACT（Activation Steering）**：推理阶段通过注入"漏洞引导向量"改变模型行为的方法，可提升 F1 至 96.25%。
5. **CPG（Code Property Graph）**：结合 AST、CFG、DFG 的统一图表示，用于结构性漏洞分析。

## C. 核心知识点（硬数字）

| 发现 | 数据 |
|------|------|
| 纳入论文 | 102 篇（从 7008 条记录筛选） |
| 发表年份分布 | 2021-2022（4 篇）、2023（12）、2024（38）、2025（41） |
| 语言分布（检测） | C（35 篇）、C++（28）、Java（21）、Python（11）、PHP（5） |
| 最常用模型 | GPT-3.5 和 GPT-4（各 30/57 篇）、Llama（24）、DeepSeek（13） |
| LLM vs SAST | LLM 常超越 SAST，但误报率更高 |
| LLM+SAST 结合效果 | IRIS：检测增 35%、误报减 80% |
| 误报率范围 | LLM：34-97%，SAST：<25-82% |
| 最佳检测 F1（微调后） | 84-99%（CodeLlama-7B 达 97%、GPT-4o-mini 达 97%） |
| 数据投毒绕过率 | CodeBreaker：92% 绕过 SAST、75% 绕过 LLM |
| Copilot 不安全代码率 | ~40%（Pearce 等） |
| ChatGPT 生成的代码 | 相比 Stack Overflow 少 20% 漏洞（Hamer 等） |
| GPT-4 修复准确率 | 93.8%（Android），Gemini 1.5 Flash 为 83.8% |
