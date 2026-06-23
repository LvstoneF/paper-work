# QASecClaw 精读笔记

> QASecClaw: A Multi-Agent LLM Approach for False Positive Reduction in Static Application Security Testing
> arXiv:2605.01885v1 | 2026-05 | Ameen, Alam, Islam (Univ. of Rajshahi, Bangladesh)

---

## A. 大白话总结

QASecClaw 是一个"多智能体"框架来减 SAST 误报。核心设计：Semgrep 先做广撒网扫描（保召回），然后一个 **SAST 过滤智能体**（用 Qwen 3.5 Plus）逐个审查告警，判断是真阳性还是假阳性。其他几个辅助智能体分别负责测试计划、证据关联、报告生成，由一个 Mission Orchestrator 统一调度。

它有个实用设计叫 **fail-open**：如果 LLM 调用失败/超时/返回格式错误，不做任何过滤，保留原始 SAST 告警——宁多报不漏报。

在 OWASP Benchmark v1.2（2740 个 Java 测试用例，11 个 CWE 类别）上，F1 从 Semgrep 的 78.39% 提升到 90.93%，误报从 560 降到 64（减少 88.6%），召回仅下降 3.1%。对注入类漏洞（SQL/XSS/命令注入）提升最大，但 CWE-501（信任边界违反）表现差（F1 下降 22.8%）。

---

## B. 术语卡片

| 术语 | 解释 |
|------|------|
| **多智能体架构** | 多个专用 LLM agent（规划/验证/过滤/报告）+ 中央编排器协同工作 |
| **SAST Filter Agent** | 核心过滤 agent：读代码上下文 + CWE 类型 → 判断 TP/FP |
| **Mission Orchestrator** | 总控：协调各 agent，管理分析流程 |
| **Fail-Open 策略** | LLM 异常时保留所有原始告警，绝不因 LLM 失败而漏掉漏洞 |
| **Evidence Correlation Agent** | 查找动态运行证据辅助验证（本评估中为静态故未启用） |
| **OWASP Benchmark v1.2** | 2740 个 Java servlet 测试用例，标注了 vulnerable/safe |
| **Youden's J** | OWASP Benchmark 的官方排名指标：J = TPR - FPR |

---

## C. 核心知识点（硬数字）

| 指标 | QASecClaw | Semgrep (基线) |
|------|-----------|----------------|
| 精确率 (Precision) | **0.951** | 0.695 |
| 召回率 (Recall) | **0.871** | 0.900 |
| F1 | **0.909** | 0.784 |
| 误报率 (FPR) | **0.048** | 0.423 |
| Youden's J | **0.823** | 0.477 |
| 误报数 (FP) | **64** | 560 |
| 假阴性 (FN) | 182 | 142 |
| 误报减少 | **88.6%** (560→64) | - |
| 召回损失 | **3.1%** (40/1273 TP 被误杀) | - |

| 其他指标 | 数值 |
|---------|------|
| 数据集 | OWASP Benchmark v1.2, 2740 Java 测试用例, 11 CWE |
| LLM 选型 | **Qwen 3.5 Plus** (API) |
| 批处理 | 每个 batch 15 个文件, 共 ~122 次 LLM 调用 |
| 管线总时间 | ~45 分钟 |
| Fail-Open 影响 | ~10-15 batch 失败/超时，保留原始告警 |
| 最佳 CWE | SQL Injection F1=94.05%, Weak Crypto F1=99.61% |
| 最差 CWE | CWE-501 Trust Boundary Violation F1=59.3% (→22.8%) |

---

## D. 综述用途

### 双轴坐标
- **横轴（补静态分析短板）**: 模式不精确（误报消减）；不做可达性/调用图
- **纵轴（健全性代价）**: 只剪误报，但有 **fail-open 保守策略**：LLM 失败时不剪任何告警。不属于"零漏报保证"但有"不会因 LLM 失败而漏报"的设计保证
- **就绪度评分**:
  - 可编译性要求: 不需要编译（Semgrep 模式匹配）— ○
  - 是否依赖云端大模型: Qwen 3.5 Plus API（云端闭源）— ●
  - 可解释性: LLM 输出 JSON 格式含 verdict — ◐
  - 真实代码验证: OWASP Benchmark（合成基准，非真实项目）— ○
  - 核心属性: **Java (OWASP Benchmark)**

### 可引硬数字
- F1 90.93% vs Semgrep 78.39%，提升 16.0%
- FP 减少 88.6%（560→64），Recall 仅降 3.1%
- 误报率从 0.423 降到 0.048
- 每个 CWE 的详细 F1 数据（Table IV）
- Fail-Open 策略是为数不多明确设计 LLM 故障兜底的论文

### 在方法演进谱系的位置
- 传统 ML 过滤（Koc 2017, Heckman 2011）→ LLM 单次过滤（LLM4SA/IRIS）→ **多智能体过滤（QASecClaw）**
- 与"保守分析"(2506.16899) 的关系：保守分析强调静态分析侧的健全性保证；QASecClaw 的 fail-open 是另一维度的保守——不让 LLM 的不稳定影响召回
- 同类对比 CodeCureAgent：CodeCureAgent 做分类+修复，QASecClaw 只做分类过滤

### 暴露的局限 / gap 贡献
1. **仅 OWASP Benchmark**：合成数据集，不是真实代码库（论文明确承认）
2. **仅 Java Web (Servlet)**：未涵盖反射/Spring/依赖注入等动态分发
3. **Qwen 3.5 Plus API 云端依赖**：离线场景不可用
4. **CWE-501 表现差**：信任边界违反的过滤需更精细的 prompt
5. **没有跨文件分析**：每个文件独立判断（论文说 batch=15 文件但属于独立处理）
6. **不处理可达性**：只做单文件的 TP/FP 判断，不做调用图可达性验证
7. **仅 Semgrep**：未与其他 SAST 工具对比
8. **无零漏报保证**：虽然 fail-open 兜底了 LLM 异常，但正常运行时 TP→FN 率 3.1% 仍存在

---

## E. 5 维矩阵（D1-D5）

| 维度 | 评分 | 说明 |
|------|------|------|
| D1: 方法新颖度 | ◐ | 多智能体架构用于 FP 消减有一定新意，但每个 agent 功能并不复杂；fail-open 设计是实用亮点 |
| D2: 实验可信度 | ◐ | OWASP Benchmark 标准基线，数据完整（含 per-CWE），但合成数据集限制；另外 ~10-15 batch fail 未被报告具体影响 |
| D3: 综述相关度 | ● | 方向③误报消减，Fail-Open 机制直接支持议程①的"保守策略"讨论 |
| D4: 可引硬数字 | ● | FP 减少 88.6%，Recall 仅降 3.1%，per-CWE 数据全面，适合对比表 |
| D5: 可复现性 | ● | 开源在 GitHub (https://github.com/takrim1999/qasecqlaw)，OWASP Benchmark 公开可用 |
