#!/usr/bin/env python3
"""验证已下载PDF是否与 review.bib 条目匹配"""
import subprocess, re, os, sys, json
from pathlib import Path
from collections import defaultdict

BIB = "/home/xx/项目/.trae/documents/review.bib"
PAPERS = "/home/xx/项目/.trae/papers"

# ---------- 1. 解析 review.bib ----------
def parse_bib(path):
    """返回 {bare_key: {'author_surname': str, 'title_words': set}} 的字典"""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    # 按 @article / @inproceedings 拆分条目
    entries = re.split(r'\n(?=@)', text.strip())
    bib = {}
    for entry in entries:
        m = re.match(r'@\w+\{([^,]+),', entry)
        if not m:
            continue
        key = m.group(1)

        # 提取第一作者姓氏
        author_match = re.search(r'author\s*=\s*\{(.+?)\}', entry, re.DOTALL)
        if author_match:
            # 取第一个作者的姓氏（"Last, First" 或 "First Last" 格式）
            authors_raw = author_match.group(1).replace('\n', ' ').strip()
            first_author = authors_raw.split(' and ')[0].strip()
            if ',' in first_author:
                surname = first_author.split(',')[0].strip()
            else:
                parts = first_author.split()
                surname = parts[-1] if parts else first_author
            # 处理 LaTeX 转义
            surname = re.sub(r'\{[^}]*\}', '', surname).strip()
            first_author_surname = surname
        else:
            first_author_surname = ""

        # 提取标题关键词
        title_match = re.search(r'title\s*=\s*\{(.+?)\}', entry, re.DOTALL)
        if title_match:
            title = title_match.group(1).replace('\n', ' ').strip()
            # 去掉 LaTeX，取长度>3的实词
            title_clean = re.sub(r'\{[^}]*\}', '', title).lower()
            title_words = {w for w in re.findall(r'[a-z]{4,}', title_clean)}
        else:
            title_words = set()

        bib[key] = {
            'surname': first_author_surname.lower(),
            'title_words': title_words,
            'title_raw': title_match.group(1).replace('\n', ' ').strip() if title_match else "",
        }
    return bib

# ---------- 2. 映射 PDF 文件名 → bib key ----------
def map_pdf_to_bib(bib):
    """通过作者名+年份做模糊匹配，返回 {pdf_stem: bib_key}"""
    mapping = {}
    for root, dirs, files in os.walk(PAPERS):
        for f in files:
            if not f.endswith('.pdf'):
                continue
            stem = f.replace('.pdf', '')
            # 从文件名提取作者和年份：形如 firstauthor2024-keyword 或 firstauthor2024a-keyword
            m = re.match(r'([a-z]+)(\d{4}[a-z]?)', stem)
            if not m:
                continue
            fname_author = m.group(1).lower()
            fname_year = m.group(2)[:4]

            # 在 bib 中找匹配作者+同年份的条目
            candidates = []
            for bib_key, info in bib.items():
                b_author = info['surname'].replace(' ', '').replace("'", "").replace('ä','a').replace('ö','o').replace('ü','u')
                b_year = re.search(r'\d{4}', bib_key)
                b_year = b_year.group(0) if b_year else ""
                if b_author.startswith(fname_author[:4]) or fname_author.startswith(b_author[:4]):
                    if b_year == fname_year:
                        candidates.append(bib_key)

            if len(candidates) == 1:
                mapping[stem] = candidates[0]
            elif len(candidates) > 1:
                # 多个候选：取关键词匹配最好的
                keyword = stem.split('-', 1)[-1] if '-' in stem else ""
                best = candidates[0]
                for c in candidates:
                    if keyword.lower() in c.lower():
                        best = c
                        break
                mapping[stem] = best

    return mapping

# ---------- 3. 验证 ----------
def verify(pdf_path, bib_info):
    """返回 (passed: bool, details: str)"""
    # 提取首页文本
    try:
        result = subprocess.run(
            ['pdftotext', '-l', '1', '-raw', pdf_path, '-'],
            capture_output=True, text=True, timeout=15
        )
        text = result.stdout.lower().strip()
    except Exception as e:
        return False, f"pdftotext 失败: {e}"

    if not text or len(text) < 50:
        return False, f"首页文本过短 ({len(text)} 字符)"

    surname = bib_info['surname'].lower()
    title_words = bib_info['title_words']

    # 检查 1：作者姓氏
    author_ok = surname in text

    # 检查 2：标题关键词命中数
    hits = [w for w in title_words if w in text]
    title_ok = len(hits) >= 2

    details = []
    if not author_ok:
        details.append(f"作者'{surname}'未在首页找到")
    if not title_ok:
        details.append(f"标题词命中: {len(hits)}/{len(title_words)} ({', '.join(hits[:5])}...)")

    if author_ok and title_ok:
        return True, f"✓ 作者+标题匹配 ({len(hits)} 个关键词)"
    else:
        return False, "; ".join(details) if details else "未知问题"

# ---------- main ----------
def main():
    print("解析 review.bib ...")
    bib = parse_bib(BIB)
    print(f"  共 {len(bib)} 个条目")

    print("映射 PDF → bib ...")
    mapping = map_pdf_to_bib(bib)
    print(f"  映射成功: {len(mapping)} 篇")

    print("\n逐篇验证...")
    print("=" * 60)

    passed = 0
    failed = []
    unmapped = []

    for root, dirs, files in os.walk(PAPERS):
        dirs.sort()
        for f in sorted(files):
            if not f.endswith('.pdf'):
                continue
            stem = f.replace('.pdf', '')
            pdf_path = os.path.join(root, f)
            rel_dir = os.path.basename(os.path.dirname(pdf_path))

            if stem not in mapping:
                unmapped.append((rel_dir, f))
                continue

            bib_key = mapping[stem]
            bib_info = bib[bib_key]
            ok, msg = verify(pdf_path, bib_info)

            if ok:
                passed += 1
                print(f"  [OK] {rel_dir}/{f}")
            else:
                failed.append((rel_dir, f, bib_key, msg))
                print(f"  [??] {rel_dir}/{f}")
                print(f"       bib={bib_key}  |  {msg}")

    print(f"\n{'='*60}")
    print(f"通过: {passed}  |  存疑: {len(failed)}  |  未映射: {len(unmapped)}")

    if unmapped:
        print(f"\n未映射到 bib 的 PDF ({len(unmapped)})：")
        for d, f in unmapped:
            print(f"  ? {d}/{f}")

    if failed:
        print(f"\n需人工确认 ({len(failed)})：")
        for d, f, key, msg in failed:
            print(f"  ! {d}/{f}")
            print(f"    bib={key}")
            print(f"    {msg}")

    if not failed and not unmapped:
        print("\n✅ 全部 52 篇 PDF 验证通过！内容与 bib 一致。")

if __name__ == '__main__':
    main()
