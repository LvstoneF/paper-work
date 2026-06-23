# 精读笔记：Evaluating Large Language Models for Line-Level Vulnerability Localization

## A. 大白话总结（3-5 句）

这是首个对 LLM 进行行级漏洞定位（AVL）的大规模系统评估，测试了 19 个 LLM（60M 到 70B 参数），涵盖三种架构和三种范式（few-shot 提示、判别式微调、生成式微调）。判别式微调效果最佳，F1 达 63.8%，大幅超越此前方法。但 LLM 对"未见项目"泛化仍差，对新发现漏洞（训练数据 cutoff 后的）精度骤降。作者提出滑动窗口和右前向嵌入两种策略缓解输入长度和单向上下文问题，F1 提升最高 29.7%。

## B. 术语卡片

1. **AVL（Automated Vulnerability Localization）**：自动漏洞定位——不仅判断有无漏洞，还要精确定位到具体行（statement 级别）。
2. **判别式微调（Discriminative Fine-tuning）**：序列标注方法，给每行代码打上"是否漏洞行"标签，适合模型微调。
3. **生成式微调（Generative Fine-tuning）**：输出结构化文本（如"漏洞在 3、5、7 行"），低数据场景更具竞争力。
4. **滑动窗口 + 右前向嵌入（Sliding Window + Right-forward Embedding）**：解决长函数输入截断和 decoder-only 单向上下文限制的改进策略。

## C. 核心知识点（硬数字）

| 发现 | 数据 |
|------|------|
| 评估 LLM 数量 | 19 个（含 GPT-4o、Claude、CodeLlama 等） |
| 模型参数范围 | 60M–70B |
| 数据集 | BV-LOC（C/C++，10,811 函数）、SC-LOC（Solidity，1,369 函数） |
| 判别式微调最佳 F1 | 63.8%（超越此前所有 AVL 方法） |
| 时序泛化基准 | BV-LOC-LF：377 个 cutoff 后披露的漏洞 |
| LLM vs 传统 DL | 提示方式下 LLM F1 不如传统 DL，但低数据场景 LLM 更优 |
| 滑动窗口提升 | 最多 F1 ↑ 29.7% |
| 跨项目泛化 | 所有模型召回率下降，大模型韧性更好 |
| 新漏洞泛化 | 精度大幅下降（不熟悉的词法和结构模式） |
| 微调范式对比 | 判别式 > 生成式（高数据），生成式 > 判别式（低数据） |
| 代码预训练架构 | encoder-only（CodeBERT）在 AVL 上表现意外好 |
