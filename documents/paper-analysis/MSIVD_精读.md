# 精读笔记：Security Vulnerability Detection with Multitask Self-Instructed Fine-Tuning of Large Language Models (MSIVD)

## A. 大白话总结（3-5 句）

MSIVD 核心思路是把漏洞代码的"标签 + 解释"同时用于多任务微调：不仅告诉 LLM 这段代码有没有漏洞，还让它学习漏洞的类型、原因、修复位置。模型用 CodeLlama-13B + PEFT/QLoRA 微调，再加一层 GNN 编码控制流图信息。在 BigVul 数据集上 F1 达 0.92（超 LineVul 的 0.81），但作者也坦承这主要因为 CodeLlama 可能已经"记住"了 BigVul——在新数据集 PreciseBugs（2023 年后漏洞）上 F1 降至 0.48。关键教训：评估 LLM 必须用 cutoff 日期后的数据。

## B. 术语卡片

1. **多任务自指导微调（Multitask Self-Instructed Fine-Tuning）**：构造"老师-学生"多轮对话数据（是否存在漏洞→解释原因→定位修复行），让 LLM 同时学习多个任务。
2. **数据泄露（Data Leakage）**：LLM 训练数据可能包含测试集中的漏洞代码——CodeLlama 在 BigVul 上预训练就达 F1 0.74，但新数据集上仅 0.22，证明存在记忆而非泛化。
3. **PEFT + QLoRA**：参数高效微调 + 4-bit 量化 LoRA，使 13B 模型能在单张 RTX 8000 上微调。
4. **LLM + GNN 混合架构**：冻结的 LLM 输出嵌入 + GNN（从控制流图提取的数据流信息）融合分类。
5. **PreciseBugs 数据集**：使用 PreciseBugCollector 自动收集 C/C++ 漏洞，时间戳截至 2023 年 1 月后，专门用于减少数据泄露。

## C. 核心知识点（硬数字）

| 发现 | 数据 |
|------|------|
| BigVul F1 | MSIVD 0.92（LineVul 0.81、CodeLlama 预训练 0.74、DeepDFA 0.67） |
| BigVul 精确率/召回率 | 0.93 / 0.91 |
| PreciseBugs F1 | MSIVD 0.48（LineVul 0.31、CodeLlama 预训练 0.22） |
| LLM 加 GNN 增益 | BigVul 上 +0.02 F1，增量有限 |
| 多轮 vs 单轮 SIFT | BigVul 上 +0.09 F1，PreciseBugs 上 +0.02 |
| BigVul 数据集 | 169,772 样本（94% 非漏洞 / 6% 漏洞） |
| PreciseBugs | 12,970 样本（80% 非漏洞 / 20% 漏洞） |
| 训练时间 | 标签-only：~2 小时到达低 loss；含解释：~16 小时 |
| 泛化差距 | CodeLlama BigVul F1 0.74 → PreciseBugs 0.22（降 70%） |
