# RealSec-bench 精读笔记

> **标题**: RealSec-bench: A Benchmark for Evaluating Secure Code Generation in Real-World Repositories
> **作者**: Yanlin Wang, Ziyao Zhang, Chong Wang, Xinyi Xu, Mingwei Liu, Yong Wang, Jiachi Chen, Zibin Zheng
> **年份**: 2026 (arXiv:2601.22706v1, Jan 2026)
> **方向**: 方向⑥ — 评测/基准
> **输出日期**: 2026-06-23

---

## A. 大白话总结

这篇论文构建了一个 **Java 安全代码生成的测试基准**——不是测 LLM 能不能检测漏洞,而是测 LLM 能不能**写出安全的代码**。

他们从 GitHub 上最热门的 4,000 个 Java 项目开始,用 CodeQL 扫出高危项目,再经过 LLM 过滤+人工审核,最终得到 105 个精心构造的任务,覆盖 19 个 CWE 类型。每个任务要求 LLM 重写一个有漏洞的函数,并且要**同时通过功能测试和安全检测**才算合格。

结果很惨:最先进的模型(Claude-3.7-Sonnet、GPT-4.1、Deepseek-V3)的**综合通过率(SecurePass@1)全部低于 6%**。模型能写出功能正确的代码,但几乎一定会引入安全漏洞。更值得关注的是:加 RAG 检索能提高功能正确性但对安全没用;在 prompt 里写安全规范反而让一些模型功能正确率下降。

一个有趣的发现是:漏洞涉及跨函数调用链越长,模型表现并不是单调下降——1 跳反而比 0 跳差,2 跳又好一些,说明模型对中间复杂度的处理极不稳定。

---

## B. 术语卡片

| 术语 | 解释 |
|---|---|
| **SecurePass@k** | 综合指标:生成的代码同时通过功能测试(Pass)和安全检测(Secure)才算合格 |
| **Secure@k** | 安全指标:两级流水线评估 — 先 CodeQL 扫,若检出则走 Multi-LLM 裁决(投票+法官) |
| **Context-Isolated Phenomenon** | 现有基准只给孤立片段而不给完整仓库上下文,导致模型能力被高估 |
| **Multi-LLM Adjudication** | 多 LLM 裁决:一组 LLM 当投票者,另一组当最终法官,判断 CodeQL 告警是 TP 还是 FP |
| **Inter-procedural Hops** | 污点分析路径中 source 到 sink 经过的中间步(赋值/函数调用)数 |
| **Dataflow Retriever** | 基于 CodeQL 的精确污点路径检索器,只返回漏洞路径涉及的函数 |
| **BM25 / Dense Retriever** | 稀疏词法检索 / 稠密语义向量检索,用作 RAG 的对比基线 |

---

## C. 核心知识点（硬数字）

### 基准构成
- **规模**: 105 个任务实例,来自 30 个 Java 仓库
- **CWE 覆盖**: 19 种 (CWE-117 日志注入 56.2% 占最多,其余包括 CWE-327 密码算法、CWE-89 SQL 注入、CWE-22 路径遍历等)
- **跨过程跳数分布**:
  - 0-hop: 35.2% (37 个)
  - 1-hop: 23.8% (25 个)
  - 2-hop: 13.3% (14 个)
  - 3-hop: 6.7% (7 个)
  - >3-hop: 21.0% (22 个) — 最极端 34 跳

### 核心结果
| 指标 | 数值 | 说明 |
|---|---|---|
| **SecurePass@1** 最优 | **5.71%** (GPT-4.1, Qwen3-235B) | 5 个模型全部 <6% |
| **Pass@1** 最优 | **16.19%** (Claude-3.7-Sonnet) | 功能正确性本身就不高 |
| **Secure@1** 最优 | **8.57%** (GPT-4.1) | 安全单独看也很低 |
| 密码学类任务 SecurePass@1 | **0.00%** | 全部模型全部失败 |
| 代码质量类任务 SecurePass@1 | **52.00%** | 这也是唯一表现尚可的类别 |

### Multi-LLM 裁决验证
- SAST 基线精度: 44.9%
- +Three Voter: 精度 63.0%,召回 85.0%,FP 降低 59.2%
- +Final Judger: **精度 81.7%,召回 98.0%,F1 89.1%,FP降低 77.6%**

### Prompt 策略对比
- **RAG 效果**: 显著提升 Pass@1(最高到 22.86% BM25),但 SecurePass@1 几乎不变(origin 5.14% → BM25 6.28% → dense 5.52% → dataflow 4.76%)
- **安全指导效果**: 模型间区别巨大 — Deepseek-V3 SecurePass@1 从 3.81%→6.67% 提升;Claude-3.7-Sonnet 反而从 4.76%→2.86% 下降,Pass@1 也从 16.19% 暴跌至 9.52%
- **Dataflow 检索器表现反常**: 作为高精度污点路径检索器,表现得反而比 BM25 和 Dense 检索器差,说明"过于聚焦漏洞路径反而丢失了功能上下文"

---

## D. 综述用途（双轴坐标 + 谱系 + gap）

### 双轴坐标
- **横轴(补静态分析短板)**: 安全代码生成评测(不是漏洞检测,但触及"生成安全代码"能力)
- **纵轴(健全性代价)**: N/A — 这是基准论文,不直接做检测
- **部署就绪度**: 基准本身针对 GPT-4.1/Claude 级云端大模型;但结论(6% SecurePass@1)说明生成安全代码远未就绪

### 关键硬数字(可引用)
- "SecurePass@1 remains below 6% across all subjects" — 可引用作"LLM 生成安全代码能力极差"的量化证据
- "the benchmark contains vulnerabilities with up to 34-hop inter-procedural dependencies" — 跨过程复杂度的量化标杆
- "RAG offers negligible benefits to security" — RAG 提升功能但不提升安全
- "Multi-LLM adjudication reduces false positives by 77.6%, achieving precision 81.7% and recall 98.0%" — 可引用为"LLM 辅助做误报过滤"的方法参考

### 方法演进谱系位置
- 之前: CyberSecEval (Bhatt 2023), CodeLMSec (Hajipour 2024), SecRepoBench (Shen 2025), CWEval (Peng 2025) — 多基于合成数据或孤立片段
- 本篇: **首个从真实仓库构建的、同时要求功能+安全的仓库级代码生成基准**
- 对比 SecRepoBench: RealSec-bench 更强调查证 pipeline(LLM 过滤+人工),且同时测功能和安全的复合指标
- **与 TOSSS 互补**: RealSec-bench 测生成, TOSSS 测选择

### 暴露的局限(对 gap 段的贡献)
1. **RAG 对安全无增益**: 即使提供精确的污点路径上下文,模型仍然生成不安全代码 — 说明问题不在上下文不足而在模型本身缺乏安全知识
2. **安全指导导致功能退化**: 加入安全规范后 Claude Pass@1 从 16.19%→9.52% — 安全和功能之间当前存在 trade-off
3. **密码学等复杂领域全面失败**: 所有模型 SecurePass@1 = 0.00% — 某些安全子领域 LLM 完全无能为力
4. **仅限 Java + Maven**: 不覆盖其他语言
5. **基准规模有限**: 105 个实例,相比 MegaVul 的万级规模较小
6. Dataflow 检索器失败说明:**"精确的静态分析路径≠足够的功能上下文"** — 这对混合架构设计有直接启示

### 对本综述的独特价值
- 与 ProjectScale 形成互补:ProjectScale 测**检测**能力,RealSec-bench 测**生成**能力,但共同结论是"LLM 在安全任务上远不可靠"
- Multi-LLM 裁决 pipeline 可为"LLM 辅助误报消减"提供方法参考
- "安全指导导致功能退化"的发现与 IRIS/保守分析的"LLM+静态混合"策略形成呼应

---

## E. 5维矩阵

| 维度 | 评级 | 说明 |
|---|---|---|
| **方法新颖度** | ● | 首个从真实仓库构建、复合指标(SecurePass@k)的仓库级安全代码生成基准,构建 pipeline 严谨 |
| **实验严谨性** | ● | 5 个模型 × 4 种策略 × 3 种 RAG,抽丝剥茧消融分析,Multi-LLM 裁决有验证(F1 89.1%) |
| **对综述的贡献** | ● | 极高——为"LLM 安全能力不足"提供量化证据;RAG 对安全无效的发现;Multi-LLM 裁决方法参考 |
| **可复现性** | ● | 公开代码和数据 (GitHub) |
| **部署就绪度** | ○ | 基准本身设计良好,但结论表明 LLM 生成安全代码远未就绪 |

> **评级**: ○ 不满足 / ◐ 部分满足 / ● 完全满足
