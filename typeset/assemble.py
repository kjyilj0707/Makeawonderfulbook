"""장별 HTML/메타 -> 최종 PDF 한 권.
사용: python3 assemble.py out_dir final.pdf ch6 ch7 ch8
(out_dir 에 build.py 결과 <ch>.html / <ch>_meta.json 이 있어야 함)
"""
import sys, os, json, re, subprocess, html as H
from pypdf import PdfReader, PdfWriter
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
OUT, FINAL, CHS = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3:]
KCSS = 'file://' + os.path.join(HERE, 'node_modules/katex/dist/katex.min.css')
CSS = 'file://' + os.path.join(HERE, 'style.css')

def page(body, extra_css=''):
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><link rel="stylesheet" href="{KCSS}">'
            f'<link rel="stylesheet" href="{CSS}"><style>{extra_css}</style></head><body>{body}</body></html>')

def render(pairs):
    args = []
    for html, pdf in pairs: args += [html, pdf]
    subprocess.run(['python3', os.path.join(HERE, 'render.py')] + args, check=True, capture_output=True)

def npages(pdf): return len(PdfReader(pdf).pages)

def page_texts(pdf):
    n = npages(pdf); out = []
    for i in range(1, n + 1):
        r = subprocess.run(['pdftotext', '-f', str(i), '-l', str(i), '-layout', pdf, '-'], capture_output=True, text=True)
        out.append(r.stdout)
    return out

metas = {c: json.load(open(os.path.join(OUT, f'{c}_meta.json'))) for c in CHS}

# ---------- 앞부분: 구성과 특징 ----------
FEATURES = '''
<h2 class="plain" style="break-before:auto">이 책의 구성과 특징</h2>
<p>강의 슬라이드(원본)의 개념·정의·공식·예제를 <b>하나도 빼지 않고</b> 개념 순서대로 다시 짰다. 원본에 없는 새 사실은 넣지 않았고, 이해를 돕는 설명·판단에는 <b>(교재 보충)</b>을 붙였다.</p>
<table><tr><th style="width:30mm">장치</th><th>모양</th><th>쓰는 법</th></tr>
<tr><td><b>개념 7-3</b></td><td>노란 번호 + 굵은 제목, 오른쪽 세로띠</td><td>원본의 절(7.3 등)과 1:1. 세로띠에 지금 개념이 늘 보인다.</td></tr>
<tr><td><b>지도</b></td><td>개념 첫머리 한 줄</td><td>장 전체 흐름 중 지금 위치(노란 칸).</td></tr>
<tr><td><b>THEME</b></td><td>테두리 번호 + 노란 밑줄 제목</td><td>원본 소제목. <b>Q</b> 질문 → 사례 → 정의 → 유도 순.</td></tr>
<tr><td><b>정리 박스</b></td><td>노란 테두리 + 노란 제목</td><td>❶❷❸ 핵심 정리. 복습 때는 이 박스만 훑는다. 마지막 줄 "한 줄로".</td></tr>
<tr><td><b>REMARK</b></td><td>검정 라벨</td><td>왜 그런가 · 기호의 뜻 · 흔한 오해 교정 · 앞뒤 연결.</td></tr>
<tr><td><b>혼동 주의</b></td><td>연노랑 면 + 검정 왼쪽 선</td><td>"A가 아니라 B" 한 문장.</td></tr>
<tr><td><b>표 읽기 · 그림</b></td><td>검정 라벨 / 회색 상자</td><td>원본 표·그래프의 구조와 볼 점.</td></tr>
<tr><td><b>[예 7-3]</b></td><td>테두리 라벨 + 회색 풀이</td><td>원본 예제 전부(원본 번호 그대로). 풀이는 고정 5단계.</td></tr>
<tr><td><b>공식 고르기</b></td><td>검정 테두리</td><td>조건에 따라 어떤 공식을 쓰는지 질문 사슬.</td></tr>
<tr><td><b>해석 틀</b></td><td>점선 상자</td><td>서술형 결론 문장의 빈칸 틀.</td></tr>
<tr><td><b>확인 예제</b></td><td>노란 원 번호 + 풀이 공간</td><td>개념 끝에 2~5문제. 정답과 풀이는 책 뒤에.</td></tr>
<tr><td><span class="tag">【태그】</span></td><td>연노랑 글씨</td><td>개념의 별명. 풀이에서 "이 줄은 이 개념 때문"을 보여 준다(장당 6개 이하).</td></tr>
<tr><td><b>원본 표기 확인</b></td><td>빨간 라벨 한 줄</td><td>원본 슬라이드의 오타·계산 불일치. 고치지 않고 표시만, 맞는 값은 "(직접 계산하면 …)".</td></tr>
<tr><td><b>출처</b></td><td>오른쪽 아래 회색</td><td>[7장 p.21] = 원본 슬라이드 쪽.</td></tr>
</table>
<h3 class="other">고정 풀이 5단계</h3>
<p>① <b>대상</b> 무엇을 구하나 → ② <b>판정</b> 어떤 조건·분포·공식인가 → ③ <b>재료</b> 표본값·자유도 → ④ <b>대입</b> 표 값과 계산 → ⑤ <b>결론</b> 해석 문장. 가설검정에서는 ①이 가설(H₀/H₁) 세우기다.</p>
<h3 class="other">공부 순서</h3>
<p>1회독: 개념 흐름대로(정리 박스·REMARK까지) → 확인 예제 풀기 → 책 뒤 정답과 풀이로 채점, 틀린 문제의 복습칸 ☐ 체크 → 2회독: 정리 박스·혼동 주의·공식 고르기만 → 시험 직전: 장 끝 <b>시험 대비 팩</b>.</p>
'''

# ---------- 차례 ----------
def toc_html(entries):
    rows = []
    for e in entries:
        if e['lvl'] == 0:
            rows.append(f'<div class="tc0"><span class="cn">{('CHAPTER ' + str(e["chap"])) if str(e["chap"]).isdigit() else e["chap"]}</span><span class="tt">{H.escape(e["title"])}</span><span class="pg">{e["page"]}</span></div>')
        else:
            lab = f'<b>개념 {e["id"]}</b>' if e.get('id') else '<b>정리</b>'
            rows.append(f'<div class="tc1">{lab}<span class="tt">{H.escape(e["title"])}</span><span class="dots"></span><span class="pg">{e["page"]}</span></div>')
    css = '''.tc0{display:flex;align-items:baseline;gap:4mm;margin:7mm 0 2mm;border-bottom:2pt solid #161616;padding-bottom:1.5mm}
.tc0 .cn{background:#F6C300;font-weight:900;padding:0 2.5mm;font-size:9pt}.tc0 .tt{font-weight:900;font-size:13pt;flex:1}.tc0 .pg{font-weight:900}
.tc1{display:flex;align-items:baseline;gap:3mm;padding:1.3mm 0 1.3mm 3mm;font-size:9.6pt}.tc1 b{min-width:19mm}.tc1 .dots{flex:1;border-bottom:.6pt dotted #aaa;margin:0 2mm}
.tc1 .pg{font-weight:700;min-width:8mm;text-align:right}'''
    return page('<h2 class="plain" style="break-before:auto">차례</h2>' + ''.join(rows), css)

# ---------- 정답과 풀이 ----------
def sol_html():
    parts = ['<h2 class="plain" style="break-before:auto">정답과 풀이</h2><div class="sol-section">']
    for c in CHS:
        m = metas[c]
        parts.append(f'<div class="sol-chapter"><span>CHAPTER {m["chap"]}</span>{H.escape(m["title"])}</div>')
        for s in m['sols']:
            parts.append(f'<div class="sol-item"><div class="sh"><span class="bd">{s["n"]:02d}</span>확인 예제 {s["n"]:02d}</div>'
                         f'<div class="ans">{s["ans"]}</div>{s["sol"]}</div>')
    parts.append('</div>')
    return page(''.join(parts).replace('class="sol-chapter"', 'class="sol-chapter" style="break-before:auto"', 1))

# ---------- 부록: 분포표 (교재 보충) ----------
def dist_html():
    z = ['<h3 class="other">표 A. 표준정규분포표 — 칸 값 = P(0 ≤ Z ≤ z)</h3><table><tr><th>z</th>' +
         ''.join(f'<th>.0{j}</th>' for j in range(10)) + '</tr>']
    for i in range(35):
        zz = i / 10
        z.append(f'<tr><td>{zz:.1f}</td>' + ''.join(f'<td>{stats.norm.cdf(zz + j/100) - 0.5:.4f}</td>' for j in range(10)) + '</tr>')
    z.append('</table>')
    al = [0.10, 0.05, 0.025, 0.01, 0.005]
    dfs = list(range(1, 31)) + [40, 60, 120]
    t = ['<h3 class="other">표 B. t분포표 — 칸 값 = t<sub>α, 자유도</sub>, P(T ≥ t) = α</h3><table><tr><th>자유도</th>' + ''.join(f'<th>α={a}</th>' for a in al) + '</tr>']
    for d in dfs: t.append(f'<tr><td>{d}</td>' + ''.join(f'<td>{stats.t.ppf(1-a, d):.3f}</td>' for a in al) + '</tr>')
    t.append('<tr><td>∞</td>' + ''.join(f'<td>{stats.norm.ppf(1-a):.3f}</td>' for a in al) + '</tr></table>')
    ca = [0.995, 0.99, 0.975, 0.95, 0.05, 0.025, 0.01, 0.005]
    x = ['<h3 class="other">표 C. 카이제곱분포표 — 칸 값 = χ²<sub>α, 자유도</sub>, P(X² ≥ χ²) = α</h3><table><tr><th>자유도</th>' + ''.join(f'<th>α={a}</th>' for a in ca) + '</tr>']
    for d in range(1, 31): x.append(f'<tr><td>{d}</td>' + ''.join(f'<td>{stats.chi2.ppf(1-a, d):.3f}</td>' for a in ca) + '</tr>')
    x.append('</table>')
    body = ('<h2 class="plain" style="break-before:auto">부록 · 분포표</h2><div class="dist"><p class="cap">(교재 보충) 아래 값은 계산으로 만든 표다. 칸의 뜻은 강의 배포 분포표와 같게 맞췄다 '
            '(표준정규: 0부터 z까지 넓이 / t·χ²: 오른쪽 꼬리 넓이 α). 시험에서는 강의에서 배포한 분포표를 기준으로 한다.</p>'
            + ''.join(z) + '<div style="break-before:page"></div>' + ''.join(t) + '<div style="break-before:page"></div>' + ''.join(x) + '</div>')
    return page(body)

# ---------- 오버레이(세로띠 + 쪽 번호) ----------
def overlay_html(labels):
    css = '''@page{size:215mm 275mm;margin:0} body{margin:0}
.pg{width:215mm;height:275mm;position:relative;break-after:page;overflow:hidden}
.bd{position:absolute;right:0;top:0;width:13mm;height:275mm;background:#F6C300}
.bd .t{position:absolute;left:0;width:13mm;top:30mm;writing-mode:vertical-rl;display:flex;align-items:center;font-weight:800;font-size:8.6pt;letter-spacing:.06em;white-space:nowrap;color:#161616}
.bd .t b{background:#161616;color:#F6C300;padding:2.2mm .8mm;margin-bottom:3mm;font-weight:900;letter-spacing:.12em}
.bd.gray{background:#CFCFCF}
.no{position:absolute;bottom:9mm;right:31mm;font-weight:900;font-size:9pt}
.no2{position:absolute;bottom:9mm;left:22mm;font-size:7.4pt;color:#8A8A8A;letter-spacing:.04em}'''
    pages = []
    for L in labels:
        if L is None: pages.append('<div class="pg"></div>'); continue
        band = ''
        if L.get('band') is not None:
            cl = 'bd gray' if L.get('gray') else 'bd'
            band = f'<div class="{cl}"><div class="t"><b>{H.escape(L["tag"])}</b>{H.escape(L["band"])}</div></div>'
        pages.append(f'<div class="pg">{band}<div class="no">{L["no"]}</div><div class="no2">통계와사회 개념서 · {H.escape(L.get("foot",""))}</div></div>')
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>' + css + '</style></head><body>' + ''.join(pages) + '</body></html>')

def w(name, s):
    p = os.path.join(OUT, name); open(p, 'w').write(s); return p

# 1) 렌더: 표지, 구성, 장, 풀이, 부록
cover_pdf = os.path.join(OUT, 'cover.pdf')
render([(os.path.join(HERE, 'cover.html'), cover_pdf)])
feat_pdf = os.path.join(OUT, 'features.pdf'); render([(w('features.html', page(FEATURES)), feat_pdf)])
ch_pdfs = []
for c in CHS:
    pdf = os.path.join(OUT, f'{c}.pdf'); render([(os.path.join(OUT, f'{c}.html'), pdf)]); ch_pdfs.append(pdf)
sol_pdf = os.path.join(OUT, 'solutions.pdf'); render([(w('solutions.html', sol_html()), sol_pdf)])
dist_pdf = os.path.join(OUT, 'dist.pdf'); render([(w('dist.html', dist_html()), dist_pdf)])

# 2) 차례 쪽수 계산 (차례는 2번 렌더: 쪽 수 확정)
def build_toc(start_pages):
    entries = []
    for c, pdf in zip(CHS, ch_pdfs):
        m = metas[c]; base = start_pages[c]
        entries.append({'lvl': 0, 'chap': m['chap'], 'title': m['title'], 'page': base})
        texts = page_texts(pdf)
        flats = [re.sub(r'\s+', '', t) for t in texts]
        for con in m['meta']['concepts']:
            key = (f'개념{con["id"]}' if con['id'] else '') + re.sub(r'\s+', '', con['title'])[:8]
            hits = [i for i, t in enumerate(flats) if i > 0 and key in t]
            pg = (hits[-1] if not con['id'] else hits[0]) if hits else 0
            if not con['id']:  # 시험 대비 팩 등: 그 제목이 쪽 맨 앞에 오는 마지막 쪽
                tops = [i for i in hits if re.sub(r'\s+', '', texts[i])[:20].find(re.sub(r'\s+', '', con['title'])[:6]) >= 0]
                if tops: pg = tops[0]
            entries.append({'lvl': 1, 'id': con['id'], 'title': con['title'], 'page': base + pg})
    entries.append({'lvl': 0, 'chap': 'ANSWER', 'title': '정답과 풀이', 'page': start_pages['sol']})
    entries.append({'lvl': 0, 'chap': 'APPENDIX', 'title': '부록 · 분포표', 'page': start_pages['dist']})
    return entries

toc_pdf = os.path.join(OUT, 'toc.pdf')
toc_n = 1
for _ in range(3):
    cur = 1 + npages(feat_pdf) + toc_n + 1  # 표지(1) 다음 쪽 번호 1부터: 구성, 차례, 장...
    start = {}
    p = npages(feat_pdf) + toc_n + 1  # 쪽 번호: 구성과 특징 = 1쪽 → 첫 장은 그다음
    for c, pdf in zip(CHS, ch_pdfs): start[c] = p; p += npages(pdf)
    start['sol'] = p; p += npages(sol_pdf); start['dist'] = p
    render([(w('toc.html', toc_html(build_toc(start))), toc_pdf)])
    if npages(toc_pdf) == toc_n: break
    toc_n = npages(toc_pdf)

# 3) 합치기 + 라벨
parts = [(cover_pdf, 'cover'), (feat_pdf, 'front'), (toc_pdf, 'front')] + [(p, c) for p, c in zip(ch_pdfs, CHS)] + [(sol_pdf, 'sol'), (dist_pdf, 'dist')]
writer = PdfWriter(); labels = []; no = 0
for pdf, kind in parts:
    r = PdfReader(pdf)
    texts = page_texts(pdf) if kind in CHS else None
    cur = None
    for i, pg in enumerate(r.pages):
        writer.add_page(pg)
        if kind == 'cover': labels.append(None); continue
        no += 1
        if kind == 'front': labels.append({'no': no, 'band': None, 'foot': '구성과 차례'}); continue
        if kind == 'sol': labels.append({'no': no, 'band': '정답과 풀이', 'tag': 'ANSWER', 'gray': True, 'foot': '정답과 풀이'}); continue
        if kind == 'dist': labels.append({'no': no, 'band': '분포표', 'tag': 'APPENDIX', 'gray': True, 'foot': '부록'}); continue
        m = metas[kind]
        flat = re.sub(r'\s+', '', texts[i])
        if i > 0:
            for con in m['meta']['concepts']:
                key = (f'개념{con["id"]}' if con['id'] else '') + re.sub(r'\s+', '', con['title'])[:8]
                ok = (key in flat) if con['id'] else flat.startswith(key)
                if ok: cur = (f'개념 {con["id"]}  ' if con['id'] else '') + con['title']
        band = cur if cur else m['title']
        labels.append({'no': no, 'band': band[:34], 'tag': f'CHAPTER {m["chap"]}', 'foot': f'제{m["chap"]}장 {m["title"]}'})
ov_pdf = os.path.join(OUT, 'overlay.pdf'); render([(w('overlay.html', overlay_html(labels)), ov_pdf)])
ov = PdfReader(ov_pdf)
for i, pg in enumerate(writer.pages):
    if labels[i] is not None: pg.merge_page(ov.pages[i])
writer.add_metadata({'/Title': '통계와사회 개념서 (6.3~8장)', '/Author': '김준엽 (개인 학습용)'})
with open(FINAL, 'wb') as f: writer.write(f)
print('pages', len(writer.pages), '->', FINAL)
