# ProjectScale 精读笔记

> **标题**: LLM-based Vulnerability Detection at Project Scale: An Empirical Study
> **作者**: Fengjie Li, Jiajun Jiang, Dongchi Chen, Yingfei Xiong
> **年份**: 2026 (arXiv:2601.19239v1, Jan 2026)
> **方向**: 方向⑥ — 评测/实证研究
> **输出日期**: 2026-06-23

---

## A. 大白话总结

这篇论文做了一个**大规模的实证研究**,把 5 个最新的 LLM 漏洞检测工具和 2 个传统静态分析工具放到真实项目上比了一轮,核心发现是：

**LLM 检测工具还远没到能用的程度**。召回率很低(C/C++ 21%, Java 34%),而且产生大量误报,即使是表现最好的工具,误报率也高达 85%。论文花 150+ 人工小时分析了 385 个误报样本,总结了一套误报根因分类法。更糟糕的是,跑一个项目要消耗数亿 token、跑几个小时到几天,成本极高。

一句话:LLM 有语义理解的优势,但当前在项目级根本不可靠,问题出在**数据流分析浅、source/sink 对不准、上下文太长模型犯迷糊**。

---

## B. 术语卡片

| 术语 | 解释 |
|---|---|
| **SFDR (Sampled False Discovery Rate)** | 抽样误报率 — 抽样的报告中误报占比 |
| **Source-Sink Mismatch** | 检测器预设的 source/sink API 和项目实际用的 API 对不上 |
| **Shallow Interprocedural Reasoning** | 只追踪有限层(如 3 层)调用链,深层路径被截断 |
| **Prompt Misalignment** | LLM 不遵守 prompt 中的 CWE 定义,偏离检测目标 |
| **RepoAudit** | 多智能体框架,从预定义 source 出发,LLM 探索调用路径到 sink |
| **IRIS** | LLM 自动标注项目中所有方法/参数为潜在 source/sink,嵌入 CodeQL 模板检测 |
| **LLMDFA** | 智能体方法,LLM 定义 source/sink 后探索所有可能路径 |
| **INFERROI** | 专门检测资源泄漏(CWE-772),LLM 推断资源意图 + CFG 路径探索 |
| **KNighter** | LLM 从漏洞修复 commit 自动生成 Clang Static Analyzer checker |

---

## C. 核心知识点（硬数字）

### 评测设置
- **被测工具**: 5 个 LLM 检测器(RepoAudit/Claude-3.5-Sonnet, KNighter/O3-mini, IRIS/GPT-4, LLMDFA/GPT-4, INFERROI/GPT-4) + 2 传统工具(CodeQL, Semgrep)
- **数据集**: 
  - 内部基准: 222 个已知漏洞,8 个 CWE 类型,C/C++ + Java
  - 真实项目: 24 个活跃开源项目
- **人工验证**: 385 个抽样报告,150+ 人工小时

### 核心数字
- **召回率**: C/C++ 平均 21.09% (27/128), Java 平均 33.82% (69/204)
- **RepoAudit 最佳**: CWE-401 召回 55%, CWE-416 仅 10%, CWE-476 仅 28.57%
- **IRIS 最佳 Java**: CWE-022 37.25%, CWE-078 46.15%, CWE-079 22.58%, CWE-094 40%
- **INFERROI** (CWE-772): 召回 62.00%,远超 CodeQL 的 10%
- **传统工具**: CodeQL 和 Semgrep 在 C/C++ 上检测 0 个漏洞(全部因为 source-sink 不匹配)
- **误报率(SFDR)**:
  - RepoAudit: 平均 97.0% (C/C++)
  - IRIS: 平均 94.4% (Java)
  - 最优工具平均: 85.3%
- **token 消耗**: 最高 225M 输入 token + 38M 输出 token (单个项目)
- **运行时间**: 最高 4,638 分钟(超过 3 天),平均 RepoAudit 448 分钟,LLMDFA 2,000 分钟

### 误报根因分布(363 个误报)
| 根因 | 占比 | 数量 |
|---|---|---|
| A1: Shallow Interprocedural Reasoning | 37.47% | 136 |
| B1: Imprecise Source/Sink Identification | 19.00% | 69 |
| D1: Missed Key Program Points | 12.67% | 46 |
| A2: Incorrect Control Flow | 6.61% | 24 |
| C1: Prompt Misalignment | 8.26% | 30 |

---

## D. 综述用途（双轴坐标 + 谱系 + gap）

### 双轴坐标
- **横轴(补静态分析短板)**: 数据流/调用图可达性 + Source/Sink 识别
- **纵轴(健全性代价)**: 只剪误报(无零漏报保证) — 论文明确证实 LLM 方法会漏报大量漏洞
- **部署就绪度**: 低 — 依赖 GPT-4/Claude 级大模型,运行成本极高,不可用于离线/等保场景

### 关键硬数字(可引用)
- "LLM-based detectors achieve average recalls of 21.09% for C/C++ and 33.82% for Java" — 实证 LLM 在项目级远非可靠
- "Even the best-performing tool still reaches an average false discovery rate of 85.3%" — 误报是实用化最大障碍
- "Shallow dataflow reasoning accounts for 37.47% of all false positives" — 跨论文可对比的根因
- "Up to 225M input tokens and 4,638 minutes runtime per project" — 成本数据

### 方法演进谱系位置
- 之前的工作: Wen et al. (VulEval), Yildiz et al. — 函数级或 commit 级评测
- 本篇定位: **首个项目级(head-to-head)对比 5 个 LLM 检测器的实证研究**,填补了"项目级实际效果未知"的空白
- 超越之前: 之前只报 P/R/F1,本篇系统分析误报根因 + 成本

### 暴露的局限(对 gap 段的贡献)
1. **LLM 的 source/sink 推断不可靠**: LLMDFA 用 few-shot 猜 API,结果 42/44 漏报源于 source-sink 不匹配
2. **浅层数据流**: RepoAudit 默认只探索 3 层调用链 — 直接验证了"静态调用图深度有限"这一核心痛点
3. **未处理 Java 框架动态分发**: 虽未明确提及反射/Spring,但 A2(Incorrect Control Flow)的示例涉及多实现函数的分发问题
4. **无任何健全性保证**: 不报漏报率/不保证零漏报
5. **仅限 C/C++ 和 Java**: 不涉及其他语言

### 对本综述的独特价值
这是 CLAUDE.md 中"跨论文主题"和"研究空白"的**直接实证支撑**——比如"静态找候选+LLM 判语义混合架构":IRIS 和 INFERROI(混合架构)比纯 LLM 方法(LLMDFA)效果更好;"数据/标注不可靠":CodeQL/Semgrep 在 C/C++ 上检 0 个漏洞;Source-sink mismatch 在 VFArche/Vercation 也反复出现,此处给出量化数据。

---

## E. 5维矩阵

| 维度 | 评级 | 说明 |
|---|---|---|
| **方法新颖度** | ◐ | 不做新方法,做实证研究,但评测范围(5+2 工具对比,222 漏洞,24 项目)是目前最全面的 |
| **实验严谨性** | ● | 150+ 人工小时验证 385 个报告,双人独立标注+一致性讨论,公开所有实验材料 |
| **对综述的贡献** | ● | 极高——直接提供"LLM 方法不可靠"的实证数据,支撑误报根因分类,量化成本瓶颈 |
| **可复现性** | ● | 公开所有脚本、prompt、标注数据和统计数据 |
| **部署就绪度** | ○ | 发现当前方法远未就绪,依赖 GPT-4/Claude,成本极高,误报率>85% |

> **评级**: ○ 不满足 / ◐ 部分满足 / ● 完全满足
