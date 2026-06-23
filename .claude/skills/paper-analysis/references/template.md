# v2 Deep-Reading Template

Every paper analysis MUST follow this exact structure.

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

## D. 对我们综述有什么用

| 用到综述哪个章节 | 用来论证什么 |
|:---|:---|
| **§X.X** Chapter name | What argument this paper supports |

---

## E. 5 维矩阵评分

| 维度 | 评分 | 白话理由 |
|:---|:---:|:---|
| D1 动态分发 | ○/◐/● | One-line justification in Chinese |
| D2 离线小模型 | ○/◐/● | ... |
| D3 零漏报保守 | ○/◐/● | ... |
| D4 动态验证 | ○/◐/● | ... |
| D5 证据链 | ○/◐/● | ... |

**一句话**：<How this paper relates to our thesis — what it covers, what gap it leaves>
```
