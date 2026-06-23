# 方向⑤ — LLM Agent 定位与可利用性验证

## 章节概述

方向⑤ 涵盖了利用 LLM Agent 进行漏洞定位、CVE 复现、可利用性验证和安全修复的 8 篇代表性工作。本章的核心叙事线是：Agent 范式从"静态定位"（T2L-Agent 的崩溃 trace → 代码行追溯）演进到"动态执行验证闭环"（VIPER-MCP/FORGE/Verify-Before-Fix 的沙盒执行确认）。2025–2026 年间，动态执行验证 (D4) 成为 Agent 方向的方法论标配，但所有 Agent 的验证目标均为"可利用性"（exploitability）而非"可达性"（reachability）——这与 SCA 审计所需的"该漏洞在当前调用图中是否可达"存在本质差异。共同局限包括：依赖云端大模型（D2 未覆盖）、无健全性保证（D3 未覆盖）、缺乏结构化可审计证据链（D5 未覆盖）。

---

## 8.1 从静态定位到执行验证闭环

### 8.1.1 静态定位的奠基：T2L-Agent

T2L-Agent (Xi et al., 2025, arXiv:2510.02389) 是方向⑤ 中最早系统化将运行时证据融入 LLM Agent 管线的工作之一。其核心设计是将漏洞定位任务拆分为两阶段：先检测"漏洞在哪段代码块"，再精确定位到具体行。关键组件是 Agentic Trace Analyzer (ATA)，它在 Docker 中编译目标程序、调用 AddressSanitizer (ASAN) 和 GDB 收集崩溃时的运行时证据（crash 日志、堆栈跟踪、内存错误详情），然后将所有证据打包为结构化"证据块"供 LLM 分析。

T2L-Agent 同时引入两项正交改进：Divergence Tracing（发散追踪）——让 LLM 从同一份证据出发生成多条独立推理路径并合并排序——和 Detection Refinement（检测精化）——两阶段"粗略→精确"的递进循环。在 50 个真实 C/C++ 开源项目漏洞的测试集（T2L-ARVO）上，最佳模型（DeepSeek V3.1）达到 53.9% 检测率和 53.4% 行级定位率。

T2L-Agent 最关键的消融结果是：**没有 ATA 时，GPT-5 和 Claude 4 Sonnet 的检测率和定位率均为 0.0%**——运行时证据不是锦上添花，而是基础前提。Divergence Tracing 则是最大的单点增益来源：GPT-5 检测率提升 13.7%、定位率提升 10.3%；Qwen3 Next 80B 的定位率暴增 48.9%。

然而，T2L-Agent 的范式局限同样明确：(i) 局限于 C/C++ 内存崩溃类漏洞（Buffer Overflow、Memory Lifecycle），完全不涉及 Java 动态分发场景；(ii) 基线配置下开源模型与闭源模型之间存在 7 倍的定位率差距（GPT-5 41.7% vs Qwen3 Next 80B 5.9%）；(iii) 不报告漏报率，无任何 fail-safe 或零漏报设计。

### 8.1.2 多 Agent 协作复现：CVE-Genie

CVE-Genie (Ullah et al., 2025, arXiv:2509.01835) 将 Agent 从"定位"推进到"全自动 CVE 复现"。给定一个 CVE 编号，系统自动下载漏洞版本源码、搭建构建环境、生成 exploit 并验证其有效性——全过程无需人工干预。其架构采用多 Agent 设计：四个模块（信息处理、环境搭建、漏洞利用、验证器）各配"开发者+批评者"两个 Agent，借助 Developer-Critic 反馈循环防止造假（critic 专门识别三类问题：建伪项目、装错版本、跳过验证）。

在 841 个 2024–2025 年发布的 CVE 上，CVE-Genie 成功复现 428 个（约 51%），平均每个成功复现花费 $2.77 和 18 分钟，覆盖 267 个开源项目、141 种 CWE 类型、22 种编程语言。最关键的消融结果：**单一最强模型（o3）在无多 Agent 协作时一个 CVE 都无法复现（0/15）**；去掉反馈循环时复现率下降 67%；去掉 critic Agent 时虚假复现增加 47%。

CVE-Genie 的方法论贡献在于提出 EAGER 准则（Exploit + Assessment + Generalization + End-to-end + Rebuild）作为理想 CVE 复现系统的标准。其多 Agent 模块化架构和 CTF Verifier 验证机制为后续 Agent 工作提供了设计模板。

局限方面：(i) 完全依赖闭源云端大模型（o3/o4-mini/Claude 等），开源模型（Qwen3、Llama 4、DeepSeek）性能差且不稳定；(ii) Builder 是最大瓶颈——失败原因 80% 是成本超限，其中 41% 卡在构建、59% 卡在生成 exploit；(iii) 仅支持 CLI 交互，不覆盖 Web UI/浏览器交互类漏洞；(iv) 对二进制/内存漏洞复现率低（桌面应用 18%、区块链 8%）。

### 8.1.3 假设验证范式：VulAgent

VulAgent (Wang et al., 2025, arXiv:2509.11523) 提出了假设验证（Hypothesis Validation）机制作为 Agent 验证的另一种路径。其核心思想是模拟人类审计员的推理方式：看到敏感操作后先构造可验证的假设（"如果 XXX 条件成立，那么 YYY 路径能触发漏洞"），然后用 Joern 提取的程序上下文（CFG/DFG/调用图）去核实每个假设。

这一设计替代了此前工作（如 VulTrial）中基于文本"反射"或"辩论"的误报过滤方式。在 PrimeVul 和 SVEN 数据集上，VulAgent 的 FPR（误报率）为 20.48%，显著优于直接评估（CoT）的 49.40% 和反射式过滤（VulTrial）的 39.76%。假设验证比反射式过滤多降约 19 个百分点的误报。

VulAgent 还贡献了一个有价值的漏洞分类洞察：按"假设难度"和"上下文依赖度"将 CWE 分为四类，揭示了不同类型漏洞的检测瓶颈差异巨大。在 GPT-4o、Qwen3-235B、DeepSeek v3.1 三个模型上均验证了框架的泛化性。

局限方面：(i) 仅 C/C++ 函数级分析，不处理 Java 动态分发；(ii) 完全依赖云端大模型 API（每样本平均 8.83 次调用）；(iii) 验证阶段以"降低 FPR"为目标，不保证零漏报——论文承认"验证器可能变得保守而隐藏真阳性"。

---

## 8.2 动态执行验证成为标配

2025 年下半年至 2026 年，方向⑤ 发生了一次方法论跃迁：以"执行验证"为核心的 Agent 架构成为主流。以下四篇论文的共同特征是——将漏洞的可利用性判定从 LLM 的推理空间转移到沙盒执行空间。

### 8.2.1 锚点定位 + 反馈进化：VIPER-MCP

VIPER-MCP (Sun et al., 2026, arXiv:2605.21392) 是首个对 MCP（Model Context Protocol）服务器做端到端安全审计的自动化框架。其设计包含两个核心技术组件：(i) **锚点查询（Anchor Query）**——用 CodeQL 两遍扫描将文件级告警精准定位到具体的 MCP 工具 handler，弥合"代码级发现"与"工具级定位"的粒度鸿沟；(ii) **反馈驱动提示进化（Feedback-Driven Prompt Evolution）**——将漏洞触发建模为自然语言 prompt 空间的搜索问题，通过双变异器调度（结构变异器处理工具选择漂移、参数变异器处理参数穿透深度）和适应度评分迭代逼近漏洞触发。

在 39,884 个真实开源 MCP 仓库中，VIPER-MCP 发现 106 个 0day 漏洞，其中 67 个已分配 CVE。误报率仅 4.6%，漏报率 7.7%，大幅优于基线 MCPSafetyScanner（43.1%/63.8%）和 Cisco AI Defense（24.6%/73.1%）。消融实验数据表明三个组件各自不可或缺：去掉锚点查询 → FNR 升至 34.6%（+26.9pp）；去掉 prompt 进化 → FNR 升至 40.8%（+33.1pp，最严重退化）；去掉变异调度 → FNR 升至 33.8%（+26.1pp）。

VIPER-MCP 的方法论核心在于"静态 CodeQL 指导动态 fuzzing"的混合范式——这与本综述脉络一（静态+LLM 互补）高度一致。但局限同样明确：(i) 仅覆盖 JavaScript/TypeScript 和 Python，不支持 Java；(ii) 仅覆盖三种污点类型（命令注入、SSRF、路径遍历），不深入 Java 特有的动态分发问题；(iii) 依赖云端大模型（GPT-5.4 系列效果最优），本地小模型未经测试。

### 8.2.2 四级分级利用：FORGE

FORGE (Shaikh, 2026, arXiv:2606.03453) 的核心创新是打破传统 PoC 生成的"成功/失败"二元结局，代之以四级分级利用分类法（Graduated Exploitation Taxonomy）：L0=无证据、L1=触发漏洞、L2=成功利用、L3=完全攻陷。系统包含 5 个 Agent（Intel → Generator → Planner → Exploit → Detector）流水线工作，其中 Exploit Agent 采用工具门控设计——前 3 轮只允许侦查，第 4 轮之后开放利用工具。

在 603 个 CVE 上，FORGE 的 67.8%（409/603）达到 L1+ 利用，每 CVE 平均成本 $1.50。一个重要的实证发现是：**EPSS 和 CVSS 分数与利用深度无显著秩相关**（Spearman ρ=0.062, p=0.13 和 ρ=0.016, p=0.71），各 EPSS 区间的利用率均约为 68%。这证明优先级元数据与代码级模式可达性是正交属性——对 SCA 领域"按 CVSS/EPSS 排序风险"的通行做法提出了质疑。

FORGE 还验证了跨 CVE 知识迁移的有效性：包级别构建失败的 48.0% 在后续同包 CVE 中被避免；CWE 级别利用死胡同的 95.5% 在后续同 CWE CVE 中被避免。Oracle 验证的 VALID 率为 92.3%（95% CI [84.8%, 96.9%]）。

局限方面：(i) 生成的是最小应用（缺乏 WAF/认证/限流等生产环境特征），L2+ 反映的是"模式级可达性"而非"部署级风险"；(ii) 不处理 Java 框架动态分发；(iii) 依赖商用闭源 LLM（Claude Sonnet 4.5 + GPT-5 Mini）。

### 8.2.3 纯 LLM 智能体：LLMVD.js

LLMVD.js (Ni et al., 2026, arXiv:2604.20179) 在方向⑤ 中占据一个独特位置——它挑战了"LLM 不够用，必须结合传统程序分析"的主流论断。系统完全依赖 LLM 推理能力（不借助 CPG、CodeQL 或符号执行），在 4 阶段流水线（Finder → Judge → Constraints Inferrer → Exploiter）中完成从扫描到 PoC 生成的闭环。

在公共基准（SecBench.js + VulcaN）上，LLMVD.js 确认了 433/517（83.75%）个漏洞，远超传统工具 Explode.js（43.13%）和 FAST（11.8%）。在 260 个新发布的 npm 包中，它挖出 36 个有效 PoC（传统工具最多 2 个）。每包平均成本仅 $0.089，有效 exploit 的摊销成本为 $0.050。

LLMVD.js 的最强论据来自转换数据集实验：对 143 个包做变量重命名和格式化后，LLMVD.js 仅丢失 1 个漏洞定位（lodash），证明其依赖的是语义理解而非表面词法模式。但对 lodash 的失效案例（8 finding → 0 finding）也暴露了 LLM 在混淆代码前的脆弱性。

这篇论文对本综述的特殊价值在于：它为"纯 LLM 在 npm 小包场景有效"提供了实证，但恰恰反衬出 Java 企业系统的挑战更大——Node.js 生态 90% 的包代码小于 32K tokens，而 Java 企业项目动辄数十万行。其结论不能简单外推到 Java SCA 场景。

### 8.2.4 执行落地的严格不变式：Verify-Before-Fix

Verify-Before-Fix (Gajjar et al., 2026, arXiv:2604.10800) 将执行验证提升为严格不变式（strict invariant）——"无执行确认，不修复"。系统由检测→验证→修复三阶段组成：先用 uAST（统一抽象语法树）结合 GraphSAGE 和 Qwen2.5-Coder 做混合检测，然后通过 Plan-Execute-Verify 循环（生成利用假设 → 构造测试程序 → 沙盒执行收集证据 → 分级判定）确认可利用性，最后用 LoRA 微调 LLM 迭代修复。

消融实验数据直接支撑了"执行验证不可省略"的设计哲学：**去掉验证环节后，不必要修复增加 131.7%，端到端成功率下降 9.56 个百分点**。验证阶段确认了 69.54% 的检测告警为可利用、拒绝了 60.51% 的误报，仅恢复了 13.95% 的漏报——说明验证阶段主要功能是过滤误报而非挽救漏报。

在跨语言场景下，uAST 将 Java/Python/C++ 的 200+ 语法类型抽象为 47 种通用节点类别，实现跨语言零样本 F1 74.43–80.12%（相比纯结构迁移提升 23.42%）。检测阶段同语言 accuracy 达 89.84–92.02%。

局限方面：(i) 仍依赖 Docker 沙盒，离线/气隙场景部署受限；(ii) 仅 2 层 GNN 表达能力有限，复杂污点流无法建模；(iii) 虽然使用 1.5B 小模型（D2 方向可取），但验证环节依赖 Docker 运行环境。

### 8.2.5 Agentic 修复的全流程闭环：CodeCureAgent

CodeCureAgent (Joos et al., 2025, arXiv:2509.11787) 将 Agent 范式应用到 SAST 告警的"分类→修复→验证"全流程。其设计包含三个子组件：Classification Sub-Agent（区分真/假阳性告警）、Repair Sub-Agent（真阳性→修复、假阳性→压制）、Change Approver（三层验证：编译通过 → 原告警消失且不新增告警 → 测试套件通过）。任何验证失败即退回重试。

在 106 个 Java 项目的 1,000 条 SonarQube 告警（覆盖 291 条规则）上，CodeCureAgent 达到 Plausible Fix 率 96.8%、人工验证 Correct Fix 率 86.3%，大幅超越规则基线 Sorald（4.3% plausible）、iSMELL（62.8%）、CORE（67.6%）。平均每条告警耗时 4.4 分钟，成本仅 2.9 美分（基于 GPT-4.1 mini）。

CodeCureAgent 的独特贡献在于：(i) 在真实 Java 项目（非合成数据）上大规模验证；(ii) 覆盖规则数量级大于此前工作（291 vs Sorald 的 30 条规则）；(iii) 三层验证大幅降低错误修复。但其局限同样与方向⑤ 的共同局限一致：依赖云端大模型（GPT-4.1 mini）、不保证零漏报（FP 分类准确率仅 81.0%）、不处理 Java 动态分发/可达性。此外，SonarQube 的告警以代码规范（code smell）为主，安全漏洞类告警仅占 3.1%。

---

## 8.3 对比分析

### 8.3.1 方法对比表

| 论文 | Agent 架构 | 输入→输出 | 执行验证 | 目标语言 | 成本 | 关键指标 |
|------|-----------|----------|---------|---------|------|---------|
| T2L-Agent (2025) | 单/多 Agent + ATA | crash trace → 漏洞行 | Docker + ASAN/GDB | C/C++ | — | GPT-5 检测 50.9%, 定位 41.6% |
| CVE-Genie (2025) | 多 Agent + Developer-Critic | CVE → verifiable exploit | Docker + CTF Verifier | 22 种语言 | $2.77/CVE | 51% (428/841) 复现率 |
| VulAgent (2025) | 多 Agent + MetaAgent | 代码片段 → 假设验证结果 | 无（纯静态） | C/C++ | — | PrimeVul ACC 58.62%, FPR 36.78% |
| VIPER-MCP (2026) | 两阶段 + 锚点查询 + 反馈进化 | MCP 仓库 → PoC + 0day | Docker + 运行时探针 | JS/TS + Python | — | 106 0day, 67 CVE, FPR 4.6% |
| FORGE (2026) | 5 Agent + 分级利用 | CVE → L0-L3 利用 + 检测规则 | 最小应用沙盒 | 8 种语言 | $1.50/CVE | 67.8% L1+, 409/603 CVE |
| LLMVD.js (2026) | 4 阶段纯 LLM | npm 包 → PoC | Oracle 执行探针 | JavaScript | $0.089/包 | 83.75% 确认率, 36 新 PoC |
| Verify-Before-Fix (2026) | Plan-Execute-Verify 循环 | 代码 → 执行确认 → 修复代码 | Docker 沙盒 | Java/Python/C++ | — | 验证消除 61.24% 误报 |
| CodeCureAgent (2025) | 3 sub-agent + 三层验证 | SAST 告警 → 修复/压制 | Build + SA + Test | Java (SonarQube) | $0.029/告警 | Plausible 96.8%, Correct 86.3% |

### 8.3.2 五维矩阵定位

| 论文 | D1 动态分发 | D2 离线小模型 | D3 零漏报保守 | D4 动态验证 | D5 证据链 |
|------|:-----------:|:------------:|:------------:|:----------:|:--------:|
| T2L-Agent | ○ | ○ | ○ | ● | ◐ |
| CVE-Genie | ○ | ○ | ○ | ◐ | ◐ |
| VulAgent | ○ | ○ | ◐ | ○ | ◐ |
| VIPER-MCP | ○ | ○ | ○ | ● | ◐ |
| FORGE | ○ | ○ | ○ | ● | ◐ |
| LLMVD.js | ○ | ○ | ○ | ● | ◐ |
| Verify-Before-Fix | ○ | ◐ | ◐ | ● | ○ |
| CodeCureAgent | ○ | ○ | ○ | ◐ | ◐ |

D4（动态执行验证）呈现出显著的聚集效应——8 篇中 5 篇获得 ●，2 篇获得 ◐。但其他四个维度几乎全面空白：
- **D1**: 所有 8 篇均为 ○——无一篇处理 Java 反射/Spring/SPI/反序列化导致的调用图断裂
- **D2**: 仅 Verify-Before-Fix 使用 1.5B 小模型（获得 ◐），其余全依赖云端大模型 API
- **D3**: Verify-Before-Fix 的严格不变式有保守倾向（获得 ◐），但无一篇做零漏报硬约束
- **D5**: 最接近的是输出 PoC 或 exploit 的论文（CVE-Genie、VIPER-MCP、FORGE、LLMVD.js 获得 ◐），但输出的 PoC 面向 exploit 复现性而非调用路径可审计性

---

## 8.4 核心发现与空白

### 发现一：D4 繁荣，但验证目标是"可利用性"而非"可达性"

方向⑤ 的最显著趋势是动态执行验证从"可选的补充"升级为"方法论的标配"。2025 年的 T2L-Agent 虽然包含 ATA 执行组件，但执行证据仍被定位为"辅助定位输入"；到 2026 年，VIPER-MCP、FORGE、Verify-Before-Fix 和 LLMVD.js 全部将执行验证作为核心不可分割的组件。Verify-Before-Fix 的消融实验（禁用验证 → 不必要修复 +131.7%）为这一趋势提供了最有力的定量支撑。

然而，**所有 Agent 回答的是"这个漏洞能否被利用"，而非"这个漏洞在目标系统中是否可达"**。前者需要构造 exploit 并在沙盒中触发——验证的是 CVE 到 exploit 的可行性。后者需要分析静态调用图并进行可达性判定——回答的是组件漏洞到应用调用点的路径是否存在。本综述的核心论点之一是：从 SCA 审计视角看，可达性是比可利用性更前置、更实用的问题。等保审计需要判定"该组件漏洞是否在应用的调用路径上"，而非"该漏洞在实验室能否被利用"。

### 发现二：Agent 全栈依赖云端大模型

8 篇论文中，7 篇完全依赖 GPT-4/GPT-5/Claude 系列等闭源云端 API 模型。仅 Verify-Before-Fix 使用 Qwen2.5-Coder-1.5B 作为检测模型——但其验证环节仍依赖 Docker 沙盒运行环境，不支持离线部署。开源模型在能力上与闭源模型的差距在多个工作中被量化：T2L-Agent 报告 7 倍定位率差距（GPT-5 41.7% vs Qwen3 5.9%）；CVE-Genie 报告开源模型在 CVE 复现上频繁出现语法错误和"只描述不执行"的问题。**没有一篇 Agent 论文评估过 ≤7B 模型在离线/气隙场景下的可用性**。

### 发现三：无健全性保证，无系统漏报报告

8 篇论文中，没有一篇将零漏报（zero false negative）作为设计目标。VIPER-MCP 在三个基线中漏报率最低（7.7%），但也无 fail-safe 机制。Verify-Before-Fix 的验证阶段仅恢复 13.95% 的漏报——意味着 86% 的检测漏报仍被漏过。**健全性代价（以漏报换误报消减）在方向⑤ 中完全未被作为评价维度**，这与本综述的双轴框架（纵轴）形成直接对照。

### 发现四：结构化证据链缺失

尽管多数论文输出 PoC 脚本、Agent 推理轨迹或分级利用等级，但没有一篇输出面向审计场景的结构化证据链——即同时包含 (i) 完整调用路径、(ii) 关键分支条件判定、(iii) LLM 判定理由、(iv) 置信度标注 的结构化数据。对于等保/合规场景而言，一份 exploit PoC 无法替代可追溯的审计证据包。这是本综述议程 5（可解释证据链与合规对接）的直接动机支撑。

### 发现五：Java 动态分发和 SCA 场景完全空白

8 篇论文中，6 篇工作在 C/C++ 或 JavaScript/TypeScript 生态，2 篇涉及 Java（CodeCureAgent 做 SonarQube 告警修复、Verify-Before-Fix 的 uAST 覆盖 Java）。但**没有一篇专门面向 Java SCA 场景**——即"给定一个包含已知 CVE 组件的 Java 企业项目，自动判定漏洞函数在该项目的调用图中是否可达"。Java 框架特有的反射/Spring 依赖注入/SPI/反序列化四种动态分发机制导致的调用图断裂，在 Agent 方向⑤ 的文献中完全没有被触及。

---

## 8.5 与议程的映射

方向⑤ 的现状与本综述的研究议程之间存在多重映射关系：

**议程 1（SCA 可达性 + 健全性）**: Agent 论文普遍解决了"可利用性验证"的方法论问题（D4 ●），但其验证目标与 SCA 可达性需求正交。将 Agent 的"执行验证"能力从可利用性判定转向可达性判定——通过运行时插桩采集真实调用图与静态调用图做差异对比——是一个方法论上可行但尚未被探索的方向。T2L-Agent 的 ATA（运行时证据采集）和 VIPER-MCP 的锚点查询（静态告警→工具 handler 映射）的设计思路可直接为议程 1 的"静态调用图主判 + LLM 补判断边"提供参考。

**议程 2（离线/小模型）**: 方向⑤ 对云端大模型的深度依赖（7/8 篇完全依赖闭源 API）暴露了离线/内网场景的空白。CodeCureAgent 的低成本（$0.029/告警）和 Verify-Before-Fix 的小模型尝试（1.5B）提示了降低算力依赖的可能性，但两者均未在离线场景下验证。

**议程 3（统一的健全性评测框架）**: 方向⑤ 没有一篇系统报告漏报率/FN（仅 VIPER-MCP 报告了 FNR 7.7%）。这与本综述双轴分析暴露的最大盲区完全一致——"现有论文几乎无人系统报告引入了多少漏报"。

**议程 4（跨语言动态分发语义建模）**: FORGE 覆盖 8 种语言、CVE-Genie 覆盖 22 种语言，验证了多语言 Agent 的可行性——但均未涉及 Java 独特的动态分发机制。跨语言 Agent 的调用图建模能力是议程 4 的技术底座。

**议程 5（可解释证据链）**: 方向⑤ 的输出形式从简单的"是/否"标签（VulAgent）演进到结构化分级（FORGE 的 L0-L3）和可复现 PoC（CVE-Genie、VIPER-MCP、LLMVD.js）——但均未达到合规审计所需的证据链格式。FORGE 的 LLM-primary Oracle 用独立模型做分级裁决、保留推理过程的设计是向议程 5 迈出的重要一步。

---

## 参考文献

本节引用论文如下（完整 BibTeX 见 `references.bib`）：

- Xi et al., "T2L-Agent: From Trace to Line — LLM Agent for Real-World OSS Vulnerability Localization," arXiv:2510.02389, 2025.
- Ullah et al., "CVE-Genie: From CVE Entries to Verifiable Exploits — An Automated Multi-Agent Framework for Reproducing CVEs," arXiv:2509.01835, 2025.
- Wang et al., "VulAgent: Hypothesis-Validation based Multi-Agent Vulnerability Detection," arXiv:2509.11523, 2025.
- Sun et al., "VIPER-MCP: Detecting and Exploiting Taint-Style Vulnerabilities in Model Context Protocol Servers," arXiv:2605.21392, 2026.
- Shaikh, "FORGE: Multi-Agent Graduated Exploitation and Detection Engineering," arXiv:2606.03453, 2026.
- Ni et al., "LLMVD.js: Taint-Style Vulnerability Detection and Confirmation for Node.js Packages Using LLM Agent Reasoning," arXiv:2604.20179, 2026.
- Gajjar et al., "Verify Before You Fix: Agentic Execution Grounding for Trustworthy Cross-Language Code Analysis," arXiv:2604.10800, 2026.
- Joos et al., "CodeCureAgent: Automatic Classification and Repair of Static Analysis Warnings," arXiv:2509.11787, 2025.
