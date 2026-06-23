# SAST-Genius 精读笔记

> LLM-Driven SAST-Genius: A Hybrid Static Analysis Framework for Comprehensive and Actionable Security
> 技术报告（未标注 arXiv ID，提交 IEEE 评审中）| 2025 | Agrawal (Google) & Ahi (Virelya Research)

---

## A. 大白话总结

SAST-Genius 是一个"Semgrep + 微调 Llama 3 8B"的混合管线。核心思路：Semgrep 做第一遍扫描产生告警，然后微调后的 Llama 3 8B 模型做智能分类（TP/FP），对确认的漏洞自动生成 PoC 利用代码。

它的特色是**端到端**：不只是分类告警，还做 exploit 验证和修复建议。在 25 个开源项目（约 25 万行代码，含 Python/Java/JavaScript）上，精确率从 Semgrep 的 35.7% 提升到 89.5%，误报从 225 降到 20，三时间减少 91%。

论文还识别了一类被传统 SAST 漏掉的"新型漏洞"（多文件数据流、回调传递、混淆密钥等），并用案例说明 LLM 如何发现这些复杂逻辑漏洞。

---

## B. 术语卡片

| 术语 | 解释 |
|------|------|
| **SAST-Genius** | Semgrep + fine-tuned Llama 3 8B 的混合 SAST 框架 |
| **Intelligent Triage Engine** | 将 SAST 告警 + 代码上下文转为结构化 prompt，让 LLM 判断是否可利用 |
| **PoC 生成 (Exploit Generation)** | 对确认可利用的漏洞自动生成 PoC 利用代码 |
| **多文件数据流** | 跨模块/跨文件的调用链，传统 SAST 常因缺乏上下文而漏报 |
| **微调 Llama 3 8B** | 用高质量安全数据集微调的 8B 参数模型，本地部署 |

---

## C. 核心知识点（硬数字）

| 指标 | 数值 |
|------|------|
| 精确率 (SAST-Genius) | **89.5%** |
| 精确率 (Semgrep 基线) | 35.7% |
| 精确率 (GPT-4 基线) | 65.5% |
| 召回率 (SAST-Genius) | **100%** |
| 召回率 (Semgrep) | 73.5% |
| 召回率 (GPT-4) | 77.1% |
| F1 (SAST-Genius) | **94.5%** |
| 误报数 (Semgrep → SAST-Genius) | **225 → 20** (~11x 改善) |
| 三时间减少 | **91%** |
| PoC 生成成功率 | ~70% |
| 基准真相 | 170 个漏洞（人工+公开报告） |
| 测试集 | 25 个 GitHub 项目, ~250K LOC (Python/Java/JavaScript) |
| LLM 选型 | **Llama 3 8B (微调)**，本地部署 |
| SAST 引擎 | Semgrep 1.97.0 |
| 新发现漏洞类型 | 多文件数据流、回调传递、SQL 注入嵌套、混淆密钥 |

---

## D. 综述用途

### 双轴坐标
- **横轴（补静态分析短板）**: 模式不精确（误报消减）+ 可解释性（PoC 验证）
- **纵轴（健全性代价）**: 只剪误报，不保证零漏报（召回 100% 是在 170 个 ground truth 上，不代表零漏报）
- **就绪度评分**:
  - 可编译性要求: 不需要编译（Semgrep 模式匹配）— ○
  - 是否依赖云端大模型: 本地 Llama 3 8B — ○
  - 可解释性: 输出推理摘要 + PoC — ◐
  - 真实代码验证: 25 个真实 GitHub 项目 — ●

### 可引硬数字
- Precision 89.5%, F1 94.5%, 225→20 FP
- Recall 100% (在 170 漏洞 ground truth 上)
- PoC 生成 70% 成功率
- 三时间 91% 减少

### 在方法演进谱系的位置
- IRIS (Naik 2024, CodeQL+GPT-4) → LSAST → **SAST-Genius (Semgrep+微调 Llama 3 8B)**
- 与"保守分析"(2506.16899) 的区别：SAST-Genius 不做健全性保证
- 与"ZeroFalse"(2510.02534) 的异同：两者都做误报消减，SAST-Genius 还做了 PoC 生成

### 暴露的局限 / gap 贡献
1. **论文质量较低**：没有 arXiv ID，参考文献格式不规范，缺少方法细节（fine-tuning 数据量、prompt 模板、训练过程均未说明）
2. **召回的疑问**：Recall 100% 在 170 漏洞 ground truth 上，但这 170 个是"确认的"漏洞，不包含未知漏洞——声称"100% 召回"有误导性
3. **没有讨论漏报率**：只报误报消减，不报告引入了多少漏报
4. **无健全性保证**：没有零漏报约束
5. **不处理 Java 动态分发**：虽然测试集含 Java 但未涉及反射/Spring DI
6. **作者背景偏行业**（Google），论文更像白皮书而非学术论文——引用时需谨慎
7. **PoC 生成 70% 成功率意味着 30% 的 TP 没有 PoC，这 30% 中可能包含不可利用的 TP → 潜在的额外误报**

---

## E. 5 维矩阵（D1-D5）

| 维度 | 评分 | 说明 |
|------|------|------|
| D1: 方法新颖度 | ◐ | Semgrep+微调 LLM 的模式常见，PoC 生成端到端有增量贡献；但方法细节不足 |
| D2: 实验可信度 | ◐ | 25 项目基准合理，但 ground truth 构建不够透明，Recall 100% 可疑 |
| D3: 综述相关度 | ● | 方向③误报消减，支持"静态+LLM 混合"趋势和"本地小模型部署"议题 |
| D4: 可引硬数字 | ◐ | Precision/F1 数据可用但需注意 Recall 100% 的局限性；无 arXiv ID 需标注"待核实" |
| D5: 可复现性 | ○ | 数据集和微调细节未公开，仅描述了框架架构 |
