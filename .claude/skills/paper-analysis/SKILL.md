---
name: paper-analysis
description: Analyze a code audit / software security academic paper and produce structured reading notes in Chinese following the v2 deep-reading template. Use this skill whenever the user asks to analyze a paper, read a paper, continue paper analysis, or mentions "精读", "论文分析", "下一篇", "接着分析". Also trigger when the user references any paper in the /papers/ directory or the paper tracking table.
---

# Paper Analysis Skill

Analyze academic papers in the code audit / LLM + software security domain and produce structured Chinese reading notes following the project's v2 deep-reading template.

## Input

A PDF file path (e.g., `/home/xx/项目/.trae/papers/direction-02-sca/paper.pdf`).

## Workflow

### Step 1: Extract paper text

```bash
pdftotext <pdf_path> -
```

If the PDF has images without embedded text, read it directly with the Read tool (with `pages` parameter).

### Step 2: Read the template and terminology

Always read these two files before writing analysis:
- `references/template.md` — the exact output format
- `/home/xx/项目/.trae/documents/术语词典.md` — pre-built terminology dictionary (60+ terms)

### Step 3: Analyze the paper

Extract key information:
- arXiv ID / DOI, year, venue
- Direction (①②③④⑤⑥)
- Problem being solved, core method, key results
- 2-5 specialized terms (check terminology dictionary first before creating new ones)
- 3-5 core knowledge points (no formulas, only conclusions + key numbers)
- Mapping to review chapters (§2-§11)
- 5-dimension matrix scores (D1-D5: ○/◐/●) with plain-language justification

### Step 4: Write output

Write to: `/home/xx/项目/.trae/documents/paper-analysis/<PaperName>_精读.md`

## Key principles

1. **Plain language first.** Every technical term gets a card: term / plain explanation / role in this paper / everyday analogy. Check `术语词典.md` first for existing definitions.
2. **No formulas, no pseudocode.** Only conclusions + key numbers (marked with 📊).
3. **3-5 knowledge points max.** Keep granularity controlled.
4. **Mapping to review.** Every finding must map to a specific review chapter.
5. **5-dimension scoring.** D1-D5 each gets ○/◐/● + one-line justification. The purpose is revealing coverage patterns, not "grading" papers.
6. **Differentiate from our work.** End with a one-sentence summary of how this paper relates to (and differs from) our thesis topic: "Java framework dynamic dispatch reachability verification with offline small models."

## The 5 dimensions

| Dim | Definition | ● | ◐ | ○ |
|-----|-----------|----|----|----|
| D1 | Java dynamic dispatch (reflection/Spring/SPI/deserialization) | Explicitly handles call-graph breakage from dynamic dispatch | Targets Java but doesn't specifically handle dynamic dispatch | Not involved |
| D2 | Offline small model (≤7B) | Uses ≤7B local model, reports offline performance | Mentions small models but main experiments use API | Online API only |
| D3 | Zero-false-negative conservative | Explicit fail-safe design, only judge "not reachable" at high confidence | Conservative leaning but not hard constraint | No such design |
| D4 | Dynamic execution verification | Runtime instrumentation/PoC execution as core validation | Indirect dynamic elements | Pure static |
| D5 | Evidence chain delivery | Structured, auditable evidence (call path + code + reasoning + confidence) | Partial evidence but not complete audit chain | Only labels/output |
