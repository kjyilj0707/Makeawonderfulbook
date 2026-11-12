"""HTML 파일들 -> PDF (Chrome). 사용: python3 render.py in1.html out1.pdf [in2.html out2.pdf ...]
CHROME_PATH 환경변수로 크롬 경로를 바꿀 수 있다 (없으면 Playwright 기본 Chromium)."""
import sys, os
from playwright.sync_api import sync_playwright

args = sys.argv[1:]
pairs = list(zip(args[0::2], args[1::2]))
with sync_playwright() as p:
    kw = {'executable_path': os.environ['CHROME_PATH']} if os.environ.get('CHROME_PATH') else {}
    b = p.chromium.launch(args=['--no-sandbox', '--allow-file-access-from-files'], **kw)
    pg = b.new_page()
    for src, out in pairs:
        pg.goto('file://' + src, wait_until='networkidle')
        pg.evaluate('document.fonts.ready')
        pg.pdf(path=out, prefer_css_page_size=True, print_background=True)
        print('ok', out)
    b.close()
