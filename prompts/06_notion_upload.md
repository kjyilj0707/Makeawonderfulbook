# 노션 업로드 (Composio Notion, CAU 워크스페이스)

마크다운 → 노션용 마크다운 변환은 [tools/to_notion_md.py](../tools/to_notion_md.py).

변환 규칙 (직접 시험해서 확인함)
- 인라인 수식 `$x$` → `` $`x`$ ``
- 블록 수식 `$$ … $$` 는 `$$` 를 **각자 한 줄**에 (한 줄짜리 `$$\begin{aligned}…$$` 는 노션에서 깨짐)
- `<details><summary>제목</summary> … </details>` → 노션 토글. 안쪽 줄은 **탭 들여쓰기**
- 긴 문서는 `## ` 경계로 ~18,000자씩 조각(part)으로 나눔

## 업로드 에이전트 프롬프트 (요약)
```
도구: Composio MCP. Notion 계정은 반드시 CAU 워크스페이스 계정.
컨테이너에서 composio로 직접 네트워크 접속은 막혀 있으니 내용은 도구 인자로 넘긴다.
입력: notion/<형식>/part01..NN.md (내용을 바꾸지 말고 그대로)
1. NOTION_CREATE_NOTION_PAGE(parent, title, icon, markdown=part01)
2. part02~ 는 같은 페이지 끝에 이어 붙인다 (마크다운 덧붙이기 도구를 찾아서). 수식·토글이 살아 있어야 한다.
3. 실패하면 그 part를 '## ' 경계에서 반으로 나눠 재시도.
4. 끝나면 블록 수·equation 블록 유무 확인.
```

에이전트가 찾은 우회
- 덧붙이기: `NOTION_UPDATE_PAGE_MARKDOWN` 으로 페이지 끝에 `APPENDMARKER` 한 줄을 두고, 다음 part가 그 줄을 바꿔치기
- 페이지를 만들 때 첫 `# 제목` 이 사라지는 경우가 있어 다시 넣음
