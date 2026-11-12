"""표준 마크다운(.md) -> Notion-flavored markdown 변환.
- 인라인 $x$  -> $`x`$
- $$ ... $$ 블록은 그대로 (한 줄짜리 $$x$$ 는 여러 줄로 펼침)
- <details><summary>T</summary> ... </details> -> 토글 (안쪽 줄은 탭 들여쓰기)
- 출력은 '## ' 제목 기준으로 잘라 여러 조각(part)으로 저장 (조각당 최대 MAXC 글자)
사용: python3 to_notion_md.py 입력.md 출력폴더
"""
import re, sys, os

MAXC = 18000

def conv_inline(line):
    # 이미 $`..`$ 형태면 그대로
    if '$`' in line:
        return line
    # $$..$$ 한 줄 블록 처리는 바깥에서
    out, i = [], 0
    pat = re.compile(r'(?<!\$)\$(?!\$)(.+?)(?<!\\)\$(?!\$)')
    return pat.sub(lambda m: '$`' + m.group(1).strip() + '`$', line)

def convert(text):
    lines = text.split('\n')
    out = []
    in_math = False
    depth = 0  # details 깊이
    for raw in lines:
        s = raw.strip()
        # details 열기/닫기
        m = re.match(r'^<details>\s*(?:<summary>(.*?)</summary>)?\s*$', s)
        if m:
            title = m.group(1) or '풀이'
            out.append('\t' * depth + f'<details>\n' + '\t' * depth + f'<summary>{conv_inline(title)}</summary>')
            depth += 1
            continue
        m2 = re.match(r'^<summary>(.*?)</summary>$', s)
        if m2 and depth > 0 and out and out[-1].endswith('<details>'):
            out[-1] = out[-1] + '\n' + '\t' * (depth - 1) + f'<summary>{conv_inline(m2.group(1))}</summary>'
            continue
        if s == '</details>':
            depth = max(0, depth - 1)
            out.append('\t' * depth + '</details>')
            continue
        ind = '\t' * depth
        # 한 줄 $$x$$
        mm = re.match(r'^\$\$(.+)\$\$$', s)
        if mm and not in_math:
            out.append(ind + '$$')
            out.append(ind + mm.group(1).strip())
            out.append(ind + '$$')
            continue
        if s == '$$':
            in_math = not in_math
            out.append(ind + '$$')
            continue
        if in_math:
            out.append(ind + s)
            continue
        if s == '':
            out.append('' if depth == 0 else ind)
            continue
        line = raw if depth == 0 else raw.lstrip()
        out.append(ind + conv_inline(line))
    return '\n'.join(out)

def split_parts(md):
    # '## ' 단위로 블록을 모아 MAXC 넘지 않게 묶음 (details/수식 중간에서 자르지 않도록 ## 경계만 사용)
    chunks, cur = [], []
    for line in md.split('\n'):
        if line.startswith('## ') and cur:
            chunks.append('\n'.join(cur)); cur = []
        cur.append(line)
    if cur: chunks.append('\n'.join(cur))
    parts, buf = [], ''
    for c in chunks:
        if buf and len(buf) + len(c) > MAXC:
            parts.append(buf); buf = c
        else:
            buf = (buf + '\n' + c) if buf else c
    if buf: parts.append(buf)
    return parts

if __name__ == '__main__':
    src, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    md = convert(open(src, encoding='utf-8').read())
    parts = split_parts(md)
    for i, p in enumerate(parts, 1):
        open(os.path.join(outdir, f'part{i:02d}.md'), 'w', encoding='utf-8').write(p)
    print(len(parts), [len(p) for p in parts])
