# ZeroFalse 精读笔记

> **标题**: ZeroFalse: Improving Precision in Static Analysis with LLMs
> **作者**: Mohsen Iranmanesh, Sina Moradi Sabet, Sina Marefat, Ali Javidi Ghasr, Allison Wilson, Iman Sharafaldin, Mohammad A. Tayebi
> **年份**: 2025
> **arXiv**: 2510.02534
> **方向**: ③ LLM 消减 SAST 误报

---

## A. 大白话总结（3-5 句）

ZeroFalse 是一个用 LLM 给 SAST 工具（CodeQL）过滤误报的框架。它把 CodeQL 产出的 SARIF 告警做结构化增强——补上数据流路径、CWE 专属知识、代码切片——然后交给 LLM 做"是/否误报"判决。实验覆盖 10 个 LLM（GPT-5、Grok-4、Gemini 2.5 Pro、DeepSeek R1、Qwen3-235B 等）和两个数据集（OWASP Java Benchmark + 自采的真实项目 OpenVuln），最好的模型在 OpenVuln 上达到 F1=0.955（gpt-5）。核心发现：**CWE 专属提示远好于通用提示**，而且推理型模型（gpt-5、grok-4）比纯大参数模型（Gemini 2.5 Pro、Qwen3-235B）在实际代码上的泛化性好得多。

## B. 术语卡片（3-5 个）

- **SARIF**: Static Analysis Results Interchange Format，静态分析结果的标准交换格式，CodeQL 会用它输出告警位置、严重度、CWE 映射、source-to-sink 数据流路径。
- **CWE 微判据 (Micro-Rubric)**: ZeroFalse 为每个 CWE 类别定制的 10-20 条声明式规则，列举高风险模式、安全惯用法、常被误认为消毒的操作。不是通用提示，而是 CWE 专属的"判决指南"。
- **CWE 专属提示 (CWE-Specific Prompting)**: 论文核心假设——"一种提示走天下"不是最优解。不同漏洞类（SQL 注入 vs XSS 等）需要不同的评判标准，因此 ZeroFalse 按 CWE 构建不同的提示模板。
- **确定性解码 (Deterministic Decoding)**: temperature=0 + JSON schema 约束输出，确保相同输入产生相同输出，结果可复现。

## C. 核心知识点（3-5 个，只留结论和硬数字）

1. **ZeroFalse 管道**: CodeQL 生成告警 → SARIF 规范化 → 上下文富（数据流路径 + 代码切片 + CWE 元数据） → CWE 专属提示构建 → LLM 判决（JSON 输出）→ 审计跟踪。设计原则：证据门控、确定性模板、schema 约束、CWE 感知。

2. **最佳模型性能**:
   - OWASP 上: grok-4 F1=0.912（P≈0.98, R>0.85）, gemini-2.5-pro F1=0.910, gpt-oss-20b Recall=0.900
   - OpenVuln 上: gpt-5 F1=0.955（P=1.0, R=0.914）, grok-4 F1=0.923, gpt-oss-20b F1=0.904
   - Gemini 2.5 Pro 在 OpenVuln 上崩塌: F1=0.372（P=1.0 但 R=0.229）——证明合成基准测试不能预测真实性能

3. **提示工程影响（RQ2）**: 优化提示（带数据流 + CWE rubric + 判决清单）相比基线（仅本地代码片段）在 OpenVuln 上带来巨大提升。gpt-5 提升 +0.334（F1）、gpt-oss-20b 提升 +0.381。**结构化上下文比原始上下文窗口大小更重要**。

4. **上下文窗口 ≠ 性能**: Gemini 2.5 Pro 有 1000K token 窗口但 OpenVuln 上 F1=0.372；gpt-5 仅 400K 窗口却 F1=0.955。关键在于**上下文利用效率**而非原始容量。

5. **CWE 表现差异**: 注入类和 XSS 被前沿模型几乎完美检测；CWE-327（密码学弱点）和 CWE-501（信任边界违反）只有 gpt-5 和 grok-4 保持高分，其余模型接近零分。

## D. 综述用途

### ① taxonomy 归类 + 双轴坐标

- **方向**: ③ LLM 消减 SAST 误报
- **横轴**: 模式不精确（误报消减）——ZeroFalse 用 LLM 语义理解来消减 CodeQL 因保守近似产生的误报。核心做法是"CodeQL 出候选 + LLM 判语义"，与保守分析、LLM4SA、LLM4FPM 同属一个谱系。
- **纵轴**: D3◐ ——**继承保守分析 fail-safe 思想**：框架设计的核心目标是"保持覆盖率不降低"（preserving coverage），不是激进消减。JSON 输出的 Confidence 字段（High/Medium/Low）给开发者保留判断权。F1 结果中 Precision 极高（多数模型 ≈0.98-1.0）但 Recall 部分模型偏低——说明设计偏向保守（宁愿留下真告警也不要漏报）。**但论文没有"零漏报"硬保证**，也没有单独报告 FN 率。因此纵轴位置是 D3（只剪误报/声称两者兼顾之间，偏谨慎）◐。

### ② 可引硬数字

- "ZeroFalse achieves F1=0.955 on OpenVuln dataset with gpt-5, and F1=0.912 on OWASP with grok-4"（Section 4.2, Abstract）
- "CWE-specialized prompting consistently outperforms generic prompts across all models"（Section 4.3, Table 4: gpt-oss-20b Δ=+0.381 on OpenVuln）
- "gemini-2.5-pro drops from F1=0.910 on OWASP to F1=0.372 on OpenVuln, a 59% decline"（Section 4.2, Section 5）
- "Optimized prompt reduced API call failures by 50% for mixtral-8x7b (from 14 to 7 context overflow failures)"（Section 4.3）
- OpenVuln dataset: 7 real-world Java projects, 58 total alerts (23 True Vulnerabilities, 35 False Positives)（Table 2）
- "SARIF serves as central interface between static analyzers and LLM adjudication"（Section 2.2）

### ③ 在方法演进谱系的位置

该论文明确将自己的工作置于 **LLM4SA → LLM4FPM → ZeroFalse** 的演进路径上：
- **LLM4SA**（Wen 2024）：首个 LLM 消减静态分析误报的工作，81% precision, 94% recall，但仅限于内存相关 bug，统一提示策略，无 CWE 区分。
- **LLM4FPM**（Chen 2024）：在 LLM4SA 基础上引入行级代码切片，但仅涉及 6 个 CWE，仍主要聚焦内存漏洞。
- **ZeroFalse**: 扩展 CWE 覆盖到 10 类、覆盖更多 LLM（10 个）、引入 SARIF 原生支持（前两者没有）、CWE 专属提示、流敏感标注。

### ④ 暴露的局限 / 对 gap 段的贡献

- **仅限 CodeQL / Java**: 实验只在 CodeQL + Java 上完成（虽声称扩展性，但未验证其他语言/工具）。
- **无健全性硬约束**: 论文提到"保持覆盖"但没给出"零新增漏报"的保证，也没有系统报告每条被过滤告警是否会引入漏报。这是双轴纵轴部分的关键空白。
- **依赖云端大模型**: 最好的模型（gpt-5、grok-4）都是闭源付费模型，小模型（mixtral-8x7b）表现极差——直接验证了**研究议程 2（离线/小模型可行性）** 的必要性。
- **OpenVuln 数据集规模小**: 只有 58 个告警，7 个项目——与 Vercation 或 VFArche 的大规模评估有差距。
- **基准与真实世界差距**: 论文自身指出 OWASP 包含"带注释、变量名描述性"的合成代码，它不代表生产代码的噪声水平。这呼应了**研究议程 3（统一健全性评测框架）** 和**议程 5（合规对接）**。

## E. 5 维矩阵评分

| 维度 | 评分 | 理由 |
|------|------|------|
| D1 数据/标注质量 | ● | 使用 OWASP 标准基准（含 ground truth）+ 构建 OpenVuln 真实项目标注（通过 patch 比对）。标注流程可靠。 |
| D2 调用图完整性 | ◐ | 框架依赖 CodeQL 的 source-to-sink trace，但自身不做调用图构建或补充断边。对动态分发（反射/Spring）无处理。 |
| D3 健全性代价 | ◐ | 设计目标是"保持覆盖率"，但无零漏报硬约束。通过 Confidence 字段保留人工复审通道，但未单独报告 FN 指标。 |
| D4 可部署性 | ◐ | 有 SARIF 标准接口、确定性输出、CI/CD 兼容性设计。但依赖云端大模型（最佳模型 GPT-5/Grok-4），在线/气隙场景不可用。 |
| D5 可解释性 | ◐ | 输出 JSON 结构含 Confidence、Sanitization Found?、Attack Feasible?，有一定结构化解释性。但缺少可视化调用路径输出。 |
