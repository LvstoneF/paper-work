# CodeCureAgent 精读笔记

> CodeCureAgent: Automatic Classification and Repair of Static Analysis Warnings
> arXiv:2509.11787v5 | 2026-04 | Joos, Bouzenia, Pradel (CISPA Helmholtz Center)

---

## A. 大白话总结

CodeCureAgent 用一个 LLM 智能体来自动完成"分类告警 → 修复真阳性 / 压制假阳性 → 验证修改"的完整流程。它不靠硬编码规则，而是让 LLM agent 通过工具（读文档、查引用、搜代码）自主探索代码仓库，然后提修复方案。

相比前人工作，它有三个关键区别：
1. **先分类再处理**：区分 TP（真阳性）和 FP（假阳性），FP 只需要压制（加注释），TP 才需要真正修。
2. **能修多文件**：修复涉及跨文件改动时也能处理，超越了此前只能改单文件的方法。
3. **三层验证**：build 通过 → 原告警消失且不新增告警 → 测试套件通过。不过就退回让 agent 重试。

在 106 个 Java 项目的 1000 条 SonarQube 告警上测试，覆盖 291 条不同规则。plausible fix 率 96.8%，人工验证正确修复率 86.3%，远超 Sorald (69.4%)、iSMELL (62.8%)、CORE (67.6%)。每条告警耗时约 4 分钟，成本 2.9 美分。

---

## B. 术语卡片

| 术语 | 解释 |
|------|------|
| **Agentic 框架** | LLM 自主决策+循环调用工具（读代码、查文档、改文件），而非被动回答 |
| **Classification Sub-Agent** | 负责判断告警是 TP 还是 FP 的子智能体，探索代码上下文后给出 verdict |
| **Repair Sub-Agent** | 负责实际修改代码的子智能体：TP→修复，FP→压制 |
| **Change Approver** | 三层验证：编译、重新静态分析（告警消失+不新增）、跑测试 |
| **Plausible Fix** | 通过了三层验证的修复（但不一定语义正确，需人工确认） |
| **Correct Fix** | 人工确认语义正确、符合规则的修复 |
| **NOSONAR** | SonarQube 的告警压制注释，加在告警行末尾 |
| **@SuppressWarnings** | Java 注解形式的告警压制 |

---

## C. 核心知识点（硬数字）

| 指标 | 数值 |
|------|------|
| 数据集 | 106 个 Java 项目, 1,000 条 SonarQube 告警, 291 条不同规则 |
| 全部代码量 | ~61K 项目（Sorald 数据集的子集） |
| Plausible Fix 率 | **96.8%** (968/1000) |
| TP 分类准确率 | 97.4% (手动验证 191 例) |
| FP 分类准确率 | 81.0% (手动验证 100 例) |
| 整体分类准确率 | **91.8%** |
| 正确修复率 (Correct Fix) | **86.3%** |
| 单行修复占比 | 52.0% (520/1000) |
| 多行修复占比 | 44.4% (444/1000) |
| 多文件修复占比 | 3.6% (36/1000) |
| 单行 Plausible 率 | 99.4% |
| 多文件 Plausible 率 | 75.0% |
| 平均耗时 | **4.4 分钟/告警**（未修复的 14.0 分钟） |
| 平均 token 消耗 | 139K tokens/告警（仅 3% 为 output） |
| 平均成本 | **2.9 美分/告警** (GPT-4.1 mini) |
| 与 Sorald 对比 (全量) | 96.8% vs 4.3% plausible |
| 与 iSMELL 对比 | 96.8% vs 62.8% plausible |
| 与 CORE 对比 | 96.8% vs 67.6% plausible |
| 消融: 无验证 | Plausible 降到 75.1%, 249 个错误修复漏过 |
| 消融: 仅 Build 验证 | Plausible 86.1% |
| 消融: Build+SA 验证 | Plausible 96.1% |

---

## D. 综述用途

### 双轴坐标
- **横轴（补静态分析短板）**: 误报消减（分类 + 压制）+ 修复真阳性
- **纵轴（健全性代价）**: 只剪误报（FP 压制不引入新代码），但不保证零漏报（分类阶段本身有错误率）
- **就绪度评分**:
  - 可编译性要求: 需要编译（Maven build）— ●
  - 是否依赖云端大模型: GPT-4.1 mini（闭源云端）— ●
  - 可解释性: Agent 轨迹可追溯（每个工具调用 + rationale）— ◐
  - 真实代码验证: 106 个真实 Java 项目 — ●
  - 核心属性: **Java（SonarQube）**, 不是 C/C++

### 可引硬数字
- Plausible Fix 96.8%, Correct Fix 86.3%（有监督方法里很高的值）
- 平均 2.9 美分/告警，4.4 分钟/告警
- 对比 SOTA 基线（Sorald/iSMELL/CORE）领先 29.2%-34.0%
- 291 条规则覆盖，一个数量级大于前人（Sorald 30 条规则，CORE 10 条 SonarQube 规则）
- 分类准确率 91.8%（TP 97.4%, FP 81.0%）

### 在方法演进谱系的位置
- 规则修复: Sorald (30 rules) → CORE (LLM+ranking) → **CodeCureAgent (agentic, 291 rules)**
- 智能体修复: RepairAgent → **CodeCureAgent**（增加了分类+压制+SA 专项验证）
- LLM4SA/Wen 2024 → IRIS (LLM+CodeQL) → **CodeCureAgent (端到端 agent, 不止分类还修)**
- 对比 "保守分析"(2506.16899): CodeCureAgent 不做健全性保证

### 暴露的局限 / gap 贡献
1. **仅 SonarQube + Java**：论文明确承认（Section 5），但框架设计理论上可迁移
2. **LLM 强依赖**：GPT-4.1 mini 不适用于离线/气隙场景；离线小模型未评估
3. **分类阶段仍是瓶颈**：FP 分类准确率仅 81.0%，19% 的 FP 被误判为 TP 导致浪费时间或破坏代码
4. **无健全性保证**：不保证零漏报（分类 + 修复都有错误率）
5. **多文件修复成功率低**：75.0%（vs 单行 99.4%），说明复杂修复仍是挑战
6. **不支持创建/重命名/删除文件**（论文 4.5.4 节承认）
7. **SonarQube 更偏代码规范（code smell）而非安全漏洞**：安全/漏洞类告警仅占 3.1%（论文 Table 3 显示）
8. **未涉及 Java 动态分发（反射/Spring/SPI）**：虽然是 Java 项目但不处理可达性分析

---

## E. 5 维矩阵（D1-D5）

| 维度 | 评分 | 说明 |
|------|------|------|
| D1: 方法新颖度 | ● | Agentic 框架 + 分类-修复分离 + 三层验证，端到端自主修复 SAST 告警，显著超越现有方法 |
| D2: 实验可信度 | ● | 1000 告警/106 项目/291 规则，人工验证，完整消融，开源 |
| D3: 综述相关度 | ● | 方向③误报消减的核心工作，直接支撑"agentic 范式"趋势 |
| D4: 可引硬数字 | ● | Plausible 96.8%, Correct 86.3%, 2.9 美分/告警, 多个对比基线 |
| D5: 可复现性 | ● | 代码和数据在 GitHub 和 Zenodo 开源 |
