# 精读笔记：LLM-SmartAudit — Advanced Smart Contract Vulnerability Detection

## A. 大白话总结（3-5 句）

LLM-SmartAudit 用多智能体对话系统做智能合约审计，设计了两种策略：BA（广泛分析，找未知漏洞）和 TA（定向分析，精确检测已知类型）。BA 模式用 GPT-3.5 召回率就达 74%，远超传统工具（Mythril 54%、Slither 46%）；升级到 GPT-4o + TA 模式后 F1 达 95%+。关键发现是多智能体协作能有效避免单一 LLM "退化推理"问题，且 TA 模式对传统工具难以检测的逻辑漏洞效果显著。

## B. 术语卡片

1. **BA 模式（Broad Analysis）**：广泛分析模式，让 LLM 用通用安全知识扫描合约代码，发现已知和未知的各种漏洞类型。
2. **TA 模式（Targeted Analysis）**：定向分析模式，针对特定 CWE 类型构建约束条件，精确检测已知漏洞类型。
3. **退化推理（Degeneration-of-Thought）**：单一 LLM 自反思时推理链条逐渐退化的问题，多智能体对话可缓解此现象。
4. **多智能体对话（Multi-Agent Conversation）**：多个专业化的 LLM 智能体（代码分析、漏洞识别、报告生成）协作完成审计。

## C. 核心知识点（硬数字）

| 发现 | 数据 |
|------|------|
| BA + GPT-3.5 召回率 | 74%（超越 Mythril 54%、Slither 46%、Securify 等） |
| BA 覆盖漏洞类型 | 10 种（RE/IO/USE/UD/TOD/TM/RP/TX/USU/GL） |
| GPT-4o + TA 最佳 F1 | 10 类中 7 类达 95%+，TOD 从 0%→94.7% |
| GPT-3.5 TA 改善 | TOD 从 0%→33.3%；IO 从 75%→90.9% |
| GPT-4o 零样本基线 | 比 GPT-3.5 BA 明显更高，但 TA 仍有提升 |
| 对比传统工具 | LLM-SmartAudit 在 10 类漏洞中全面领先 |
| 真实数据集 | 6,454 个合约，102 个项目（Code4rena） |
| 模型配置 | GPT-3.5-turbo / GPT-4o，temperature=0.2 |
