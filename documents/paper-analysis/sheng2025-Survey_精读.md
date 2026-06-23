# 精读笔记：LLMs in Software Security — A Survey of Vulnerability Detection Techniques and Insights

## A. 大白话总结（3-5 句）

这是一篇针对 LLM 在软件漏洞检测领域的最新综述（2025），覆盖了 58 篇高质量论文。作者问了四个问题：用了哪些 LLM、用什么数据集和指标评估、用了哪些技术、面临什么挑战。核心发现是 GPT-4 系列用得最多（29 次），C/C++ 占研究的一半，但大多数研究只分析孤立代码片段（83%），离真实仓库级检测还有距离。文章指出了数据质量差、复杂代码处理难、可解释性不足等主要障碍。

## B. 术语卡片

1. **Decoder-only LLM**：只使用 Transformer 解码器部分生成文本的模型（如 GPT-4、CodeLlama），在漏洞检测中占 67.1%，是目前主流架构。
2. **PEFT（Parameter-Efficient Fine-Tuning）**：只更新少量参数的高效微调方法（如 LoRA），大模型（>10B 参数）+ PEFT 效果最优，F1 可达 ~0.9。
3. **CoT（Chain-of-Thought）Prompting**：引导 LLM 分步推理（先总结功能 → 再评估潜在错误 → 最终判断），大模型（>10B）必用。
4. **Repository-level Detection**：在整个代码仓库级别检测漏洞（跨文件依赖），当前多数研究只能做到函数级或文件级，仓库级是重要缺口。
5. **数据泄露（Data Leakage）**：LLM 训练数据可能包含测试集中的漏洞代码，导致性能虚高——高质量数据集需要去重和版本控制。

## C. 核心知识点（硬数字）

| 发现 | 数据 |
|------|------|
| 入选论文 | 58 篇（从 500+ 筛选） |
| 目标语言分布 | C/C++ 50%、Java 21.1%、Solidity 11.8% |
| 最常用 LLM | GPT-4（29 次）、GPT-3.5（25 次） |
| 架构分布 | Decoder-only 67.1%、Encoder-only 24.2%、Encoder-Decoder 8.7% |
| 微调实验 | 65% 使用 Decoder-only 模型 |
| 代码处理技术使用率 | 41.3%（AST/CFG/RAG/切片等） |
| 孤立片段研究占比 | ~83%（约 40 篇） |
| 最佳 F1 分数 | GPT-4/CodeLlama PEFT 微调后 ~0.9 |
| 内存漏洞 | 过去五年最普遍的漏洞类型 |
| GitHub 相关漏洞 | Android（7215 CVE）、Linux Kernel（5912）、MacOS X（3206） |
| 最大数据集 | SARD >500 万项、D2A ~130 万项 |
