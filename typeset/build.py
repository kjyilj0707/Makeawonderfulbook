"""원고(.md, 마크업 규칙 D_BRIEF) -> 장별 HTML.
사용: python3 build.py ch7.md out_dir  (out_dir/ch7.html, out_dir/ch7_sol.html, out_dir/ch7_meta.json)
"""
import sys, os, re, json, subprocess, html as H
from bs4 import BeautifulSoup, NavigableString

HERE = os.path.dirname(os.path.abspath(__file__))
TAG_RE = re.compile(r'【([^】]{1,30})】')

FENCE_RE = re.compile(r'^(\s*)(:{3,})\s*([A-Za-z][\w-]*)\s*(.*?)\s*:*\s*$')

def preprocess(md_text):
    out = []
    for line in md_text.split('\n'):
        m = FENCE_RE.match(line)
        is_fence = bool(m) or re.match(r'^\s*:{3,}\s*(\{.*\})?\s*$', line)
        if m and not line.strip().startswith(':::{') :
            ind, colons, name, rest = m.groups()
            line = f'{ind}{colons} {{.{name} {rest}}}'.replace(' }', '}')
        if is_fence:
            # 펜스 앞뒤에 빈 줄 (문단에 흡수되지 않게)
            if out and out[-1].strip() != '': out.append('')
            out.append(line.strip()); out.append('')
        else:
            out.append(line)
    return '\n'.join(out)

def run_pandoc(md_path):
    src = preprocess(open(md_path, encoding='utf-8').read())
    tmp = f'/tmp/pp_{os.path.basename(md_path)}'
    open(tmp, 'w', encoding='utf-8').write(src)
    md_path = tmp
    r = subprocess.run(['pandoc', '-f', 'markdown+fenced_divs+pipe_tables+tex_math_dollars-implicit_figures',
                        '-t', 'html5', '--katex', '--wrap=none', md_path], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr)
    if r.stderr.strip(): sys.stderr.write('[pandoc] ' + r.stderr[:2000] + '\n')
    return r.stdout

def katexify(html_str, tag):
    tmp_in, tmp_out = f'/tmp/ks_{tag}_in.html', f'/tmp/ks_{tag}_out.html'
    open(tmp_in, 'w').write(html_str)
    r = subprocess.run(['node', os.path.join(HERE, 'katexify.js'), tmp_in, tmp_out], capture_output=True, text=True, cwd=HERE)
    sys.stderr.write(r.stderr)
    return open(tmp_out).read()

def new(soup, name, cls=None, text=None):
    t = soup.new_tag(name)
    if cls: t['class'] = cls if isinstance(cls, list) else [cls]
    if text is not None: t.string = text
    return t

def has_cls(t, c):
    return t.name == 'div' and c in (t.get('class') or [])

def attr(t, k):
    return t.get('data-' + k) or t.get(k) or ''

def tagify(soup):
    # 【태그】 -> span.tag (math 내부 제외)
    for s in list(soup.find_all(string=TAG_RE)):
        if s.find_parent(class_='katex') or s.find_parent('code'): continue
        parts = TAG_RE.split(str(s))
        frag = []
        for i, p in enumerate(parts):
            if i % 2 == 0:
                if p: frag.append(NavigableString(p))
            else:
                sp = new(soup, 'span', 'tag', f'【{p}】'); frag.append(sp)
        for f in frag: s.insert_before(f)
        s.extract()

def transform(html_str, chap_no, chap_title):
    soup = BeautifulSoup(html_str, 'html.parser')
    meta = {'concepts': [], 'problems': 0}
    sols = []  # (num, problem_html_summary, answer_html, solution_html)

    tagify(soup)
    stepify(soup)
    # h1 제거 (장 표지에서 따로)
    for h1 in soup.find_all('h1'): h1.decompose()

    # 장 머리 블록 라벨
    for cls, lab in (('prereq', '이 장에 필요한 앞 장 기초'), ('symbols', '기호표')):
        for d in soup.find_all('div', class_=cls):
            d.insert(0, new(soup, 'div', 'blk-label', attr(d, 'title') or lab))

    # 박스류
    for d in soup.find_all('div', class_='summary'):
        d.insert(0, new(soup, 'div', 'box-title', attr(d, 'title')))
        ps = d.find_all('p', recursive=False)
        for p in ps:
            if p.get_text().strip().startswith('한 줄로'):
                p['class'] = ['oneline']
    for cls in ('tableread', 'pick', 'figure'):
        for d in soup.find_all('div', class_=cls):
            if attr(d, 'title'): d.insert(0, new(soup, 'div', 'bx-lab', attr(d, 'title')))
    # REMARK 번호: h3마다 리셋
    rm_n = 0
    for el in soup.find_all(['h2', 'h3', 'div']):
        if el.name in ('h2', 'h3'): rm_n = 0; continue
        if has_cls(el, 'remark'):
            rm_n += 1
            head = new(soup, 'div', 'rm-head')
            head.append(new(soup, 'span', 'rm-lab', f'REMARK {rm_n}'))
            head.append(new(soup, 'span', 'rm-ti', attr(el, 'title')))
            body = new(soup, 'div', 'rm-body')
            for c in list(el.contents): body.append(c.extract())
            el.append(head); el.append(body)
    # 원본 예제
    for d in soup.find_all('div', class_='example'):
        hd = new(soup, 'div', 'ex-head'); sp = new(soup, 'span', None, f'[{attr(d, "label")}]'); hd.append(sp)
        d.insert(0, hd)

    # h2 / h3 처리
    for h in soup.find_all('h2'):
        txt = h.get_text().strip()
        m = re.match(r'개념\s*([0-9]+-[0-9A-Za-z]+)\s*(.*)', txt)
        if m:
            h.clear(); h['class'] = ['concept']
            h['id'] = 'c-' + m.group(1)
            h.append(new(soup, 'span', 'no', f'개념 {m.group(1)}')); h.append(new(soup, 'span', 'ti', m.group(2)))
            meta['concepts'].append({'id': m.group(1), 'title': m.group(2)})
        else:
            h['class'] = ['plain']
            meta['concepts'].append({'id': None, 'title': txt})
    for h in soup.find_all('h3'):
        txt = h.get_text().strip()
        m = re.match(r'THEME\s*([0-9]+)\s*(.*)', txt)
        if m:
            h.clear(); h['class'] = ['theme']
            h.append(new(soup, 'span', 'tno', f'THEME {m.group(1)}')); h.append(new(soup, 'span', 'tti', m.group(2)))
        else:
            h['class'] = ['other']

    # 시험 대비 팩 이후 섹션 표시
    for h in soup.find_all('h2', class_='plain'):
        if '시험 대비' in h.get_text():
            wrap = new(soup, 'div', 'pack')
            sib = h.next_sibling; h.insert_before(wrap); wrap.append(h.extract())
            while sib is not None:
                nxt = sib.next_sibling
                if getattr(sib, 'name', None) == 'h2': break
                wrap.append(sib.extract()); sib = nxt

    # 확인문제: 번호, 메타, 풀이 이동, 연속 묶음 머리
    n = 0
    for d in soup.find_all('div', class_='problem'):
        n += 1
        sol = d.find('div', class_='solution', recursive=False)
        ans = d.find('div', class_='answer', recursive=False)
        sol_html = sol.decode_contents() if sol else ''
        ans_html = ans.decode_contents() if ans else ''
        if sol: sol.decompose()
        if ans: ans.decompose()
        body = new(soup, 'div', 'pbody')
        meta_line = new(soup, 'div', 'meta')
        bits = []
        if attr(d, 'type'): bits.append(f'<b>{H.escape(attr(d, "type"))}</b>')
        if attr(d, 'level'): bits.append(H.escape(attr(d, 'level')))
        if attr(d, 'theme'): bits.append('근거 ' + H.escape(attr(d, 'theme')))
        meta_line.append(BeautifulSoup(' · '.join(bits) + ' · 복습 ☐☐☐', 'html.parser'))
        for c in list(d.contents): body.append(c.extract())
        body.insert(0, meta_line)
        body.append(new(soup, 'div', 'space'))
        badge = new(soup, 'div', 'badge', f'{n:02d}')
        d.append(badge); d.append(body)
        first_text = body.get_text(' ', strip=True)
        sols.append({'n': n, 'ans': ans_html, 'sol': sol_html})
    meta['problems'] = n
    # 연속된 problem 묶음 앞에 '확인 예제' 머리
    for d in soup.find_all('div', class_='problem'):
        prev = d.find_previous_sibling()
        if prev is None or not has_cls(prev, 'problem'):
            hd = new(soup, 'div', 'problems-head')
            hd.append(new(soup, 'span', 'lab', '확인 예제')); hd.append(new(soup, 'span', 'line'))
            d.insert_before(hd)

    return soup, sols, meta

STEP_RE = re.compile(r'\s*([②③④⑤])')

def stepify_node(soup, root):
    for s in list(root.find_all(string=STEP_RE)):
        if s.find_parent(class_='katex'): continue
        parts = STEP_RE.split(str(s))
        frag = [NavigableString(parts[0])] if parts[0] else []
        for i in range(1, len(parts), 2):
            frag.append(soup.new_tag('br'))
            frag.append(NavigableString(parts[i] + (parts[i + 1] if i + 1 < len(parts) else '')))
        for f in frag: s.insert_before(f)
        s.extract()

def stepify(soup):
    for d in soup.find_all('div', class_='solution'):
        stepify_node(soup, d)

PAGE = '''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<link rel="stylesheet" href="{katex_css}"><link rel="stylesheet" href="{css}"></head>
<body>{band}{body}</body></html>'''

def band_html(chap_no, short):
    return f'<div class="band"><div class="t"><b>CHAPTER {chap_no}</b>{H.escape(short)}</div></div>'

def chapter_open(chap_no, title, rng, concepts, flow_html):
    items = ''.join(f'<div><b>개념 {c["id"]}</b><span>{H.escape(c["title"])}</span></div>' for c in concepts if c['id'])
    return (f'<section class="chapter-open"><div class="num"><span>{chap_no:02d}</span></div>'
            f'<h1>{H.escape(title)}</h1><div class="range">{H.escape(rng)}</div>'
            f'<div class="flow">{flow_html}</div><div class="themelist">{items}</div></section>')

if __name__ == '__main__':
    md, outdir, chap_no, title, short = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]
    os.makedirs(outdir, exist_ok=True)
    tag = os.path.splitext(os.path.basename(md))[0]
    html_str = katexify(run_pandoc(md), tag)
    soup, sols, meta = transform(html_str, chap_no, title)
    # 장 머리: chapter-intro의 첫 문단(범위)과 화살표 문단(지도)을 표지면에 사용
    ci = soup.find('div', class_='chapter-intro')
    rng, flow = '', ''
    if ci:
        ps = ci.find_all('p', recursive=False)
        for p in ps:
            t = p.get_text()
            if not rng and ('범위' in t or '원본' in t): rng = t.strip(); p.decompose(); continue
            if not flow and '→' in t: flow = p.decode_contents(); p.decompose(); continue
    opener = chapter_open(chap_no, title, rng, meta['concepts'], flow)
    katex_css = os.path.join(HERE, 'node_modules/katex/dist/katex.min.css')
    css = os.path.join(HERE, 'style.css')
    page = PAGE.format(katex_css='file://' + katex_css, css='file://' + css,
                       band='', body=opener + str(soup))
    open(os.path.join(outdir, f'{tag}.html'), 'w').write(page)
    json.dump({'meta': meta, 'sols': sols, 'title': title, 'chap': chap_no}, open(os.path.join(outdir, f'{tag}_meta.json'), 'w'), ensure_ascii=False)
    print(tag, 'concepts', len(meta['concepts']), 'problems', meta['problems'])
