// pandoc --katex 출력의 <span class="math inline|display">TeX</span> 를 KaTeX HTML로 바꾼다.
const fs = require('fs');
const katex = require('katex');
const [,, inp, out] = process.argv;
let html = fs.readFileSync(inp, 'utf8');
const unescape = s => s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&');
let errors = 0;
html = html.replace(/<span class="math (inline|display)">([\s\S]*?)<\/span>/g, (m, kind, tex) => {
  const src = unescape(tex);
  try {
    return katex.renderToString(src, {
      displayMode: kind === 'display', throwOnError: true, strict: false, trust: false, output: 'html',
      macros: { '\\Var': '\\operatorname{Var}', '\\var': '\\operatorname{var}' }
    });
  } catch (e) {
    errors++;
    process.stderr.write(`KATEX_ERR: ${e.message.split('\n')[0]} :: ${src.slice(0, 120)}\n`);
    return `<span class="math-error">${tex}</span>`;
  }
});
fs.writeFileSync(out, html);
process.stderr.write(`katex errors: ${errors}\n`);
