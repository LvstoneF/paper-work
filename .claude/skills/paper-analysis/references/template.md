# v2 Deep-Reading Template

Every paper analysis MUST follow this exact structure.

> ⚠️ 项目性质：这是一篇**文献综述**（纯综述，无自建方法、无实验）。差异化分析的落点是**双轴框架 + 5 条研究议程**，**绝不**写「我们的方法 / 我们的实验 / 我们的靶场」。见仓库根 `CLAUDE.md`。

## Output format

```markdown
# <PaperName> 精读笔记

> arXiv: <ID> | 方向 <①②③④⑤⑥> | ★ 必引必区分 (if applicable) | <Year>

---

## A. 大白话总结

1 paragraph, 3-5 sentences. Zero technical jargon. Explain: what problem, what method, what result. Someone with zero code audit knowledge should understand.

---

## B. 术语卡片

2-5 cards. Each card format:

### 术语 N：<Term Name>
- **大白话**：One sentence explaining what it is in plain language
- **在本文中的作用**：Why this paper needs it
- **打个比方**：Everyday analogy

**Rule**: Check `/home/xx/项目/.trae/documents/术语词典.md` first. If the term already exists there, reference it instead of redefining. Only create new cards for terms NOT already in the dictionary.

---

## C. 核心知识点

3-5 knowledge points. NO formulas, NO pseudocode. Only conclusions + key numbers.

### 知识点 N：<Title>
<Explanation in plain language>

> 📊 **关键数字**：<key metrics>

---

## D. 对综述哪个章节有用

| 用到综述哪个章节 | 用来论证什么 |
|:---|:---|
| **§X.X** Chapter name | What argument this paper supports |

---

## E. 5 维矩阵评分（细粒度打分，双轴的支撑）

| 维度 | 评分 | 白话理由 |
|:---|:---:|:---|
| D1 动态分发 | ○/◐/● | One-line justification in Chinese |
| D2 离线小模型 | ○/◐/● | ... |
| D3 零漏报保守 | ○/◐/● | ... |
| D4 动态验证 | ○/◐/● | ... |
| D5 证据链 | ○/◐/● | ... |

---

## F. 双轴定位 + 议程映射（综述核心分析工具）

| 项 | 内容 |
|:---|:---|
| **横轴**（LLM 补静态分析哪个短板） | 调用图不完整(可达性) / 模式不精确(误报) / 污点规范缺失(source-sink) / 版本与可达性鸿沟 / 数据与标注质量 —— 选一并说明 |
| **纵轴**（对健全性 soundness 的代价） | 只剪误报(可能引入漏报) / 只补漏报 / 声称两者兼顾 / 有无「零漏报」保证 —— 选一并说明 |
| **部署就绪度** | 可编译性要求：<> ／ 云端大模型依赖：<> ／ 可解释性：<> ／ 真实代码库(非合成)验证：<> |
| **方法演进谱系位置** | 在哪条技术脉络的哪个节点（如 V0Finder→V-SZZ→VERCATION，语法→语义） |
| **对应研究议程** | 议程N（本文印证/暴露了该议程的哪个空白；议程编号见 CLAUDE.md：1 健全性 SCA 可达性 / 2 离线小模型 / 3 健全性评测 / 4 跨语言动态分发 / 5 证据链合规） |

**一句话（双轴坐标 → 议程空白）**：本文落在【横轴X × 纵轴Y】、部署就绪度【高/中/低】；它印证/暴露了**议程N**的空白——<具体说明这篇补了什么、还差什么>。
```

> **收尾铁律**：F 节的「一句话」只能写「本文落在双轴何处、对应/暴露议程几的空白」，**不得**出现「我们的方法/我们的工作/正文论文要做……」这类原创论文叙述。要表达「这块没人做」时，写成「**议程N 指出的空白**」。
