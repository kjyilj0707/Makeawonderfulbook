# 3단계 채점 지시서

## 역할 1: 시험 응시자 (solver)
- 읽을 수 있는 파일: 담당 샘플 1개(/home/claude/proj/samples/sample_<코드>_7장.md) + /home/claude/proj/eval/exam.md **뿐**.
- 원본 PDF, 다른 샘플, exam_key.md, concepts.md, rubric.md, specs 는 절대 열지 마라. 너의 사전 지식도 쓰지 말고 **샘플에 적힌 내용만으로** 풀어라. 샘플에서 근거를 못 찾으면 "근거 없음"이라 적고 추측 답을 따로 표시.
- 출력: /home/claude/proj/eval/answers_<코드>.md — 문항별 답, 풀이 요약, 샘플 근거 위치(제목/줄 인용 10단어 이내).

## 역할 2: 감사자 (auditor)
- 읽는 파일: /home/claude/proj/eval/rubric.md, concepts.md, 담당 샘플, 원본 텍스트(/home/claude/src/tongsa/txt/통계사회_제7장.txt, 통계사회_7장보충.txt)와 슬라이드 그림(/home/claude/proj/work/ch7/). exam 관련 파일은 열지 마라.
- 할 일 (rubric.md 기준 그대로):
  1. 누락: concepts.md 99개 항목을 하나씩 샘플에서 찾아 있음/부분/없음 표.
  2. 정확성: 샘플 안의 원본과 다른 사실·틀린 수식·계산 오류 목록 (원본 자체 오류를 원본대로 썼거나 정정을 밝힌 것은 감점 아님).
  3. 이해 용이성: 통계 배경 없는 대학 1학년 관점에서 막히는 지점(심각/보통/경미) 목록.
  4. 정성 평가: 형식의 장점 3, 단점 3, 다른 장에 확장할 때 위험 1~2.
- 출력: /home/claude/proj/eval/audit_<코드>.md — 각 항목 점수(누락 /25, 이해 /15, 정확성 감점)와 근거 표.
- 최종 답: 세 점수와 장단점 각 한 줄.
