# AI 에이전트 입문: while 문에서 에이전트 팀까지

유튜브 강의 시리즈의 예제 코드 저장소예요.
파이썬 반복문 하나로 시작해서, 편마다 **점심 결정 에이전트**에 기능을 하나씩 붙여 마지막엔 에이전트 여러 명이 협업하는 팀까지 만들어요.

- 대상: 파이썬 기초 문법을 아는 입문~초급 개발자
- 프레임워크 없이 순수 파이썬 + Gemini 공식 SDK만 써요
- 폴더 안의 `*_실행기록.txt`는 영상에 나온 **실제 실행 결과**예요

## 강의 목록

| 편 | 제목 | 코드 | 영상 |
|---|---|---|---|
| 1 | AI 에이전트, 사실 while 문 하나야 | [01-agent-loop](01-agent-loop) | 공개 예정 |
| 2 | 에이전트에게 기억을 붙이자 | 준비 중 | |
| 3 | 모델이 잘 쓰는 도구는 따로 있다 | 준비 중 | |
| 4 | 에이전트가 정답이 아닐 때: 워크플로 패턴 5가지 | 준비 중 | |
| 5 | 생각 먼저, 행동은 나중에: 계획하는 에이전트 | 준비 중 | |
| 6 | 스스로 검토하는 에이전트: 반성 | 준비 중 | |
| 7 | 모르는 건 찾아보게 하자: 지식 검색(RAG) | 준비 중 | |
| 8 | 도구를 USB처럼 꽂아 쓰기: MCP | 준비 중 | |
| 9 | 에이전트 여러 명이 팀을 짜면 | 준비 중 | |
| 10 | 팀이 망가지는 이유와 고치는 법 | 준비 중 | |

## 실행 방법

```bash
pip install -r requirements.txt
```

[Google AI Studio](https://aistudio.google.com/apikey)에서 Gemini API 키를 받아 환경변수에 넣어 주세요.

```bash
# macOS / Linux
export GOOGLE_API_KEY="여기에_키"
# Windows PowerShell
$env:GOOGLE_API_KEY="여기에_키"
```

```bash
cd 01-agent-loop
python lunch_agent.py
```

> ⚠️ Gemini 무료 사용량은 모델마다 하루 횟수 제한이 있어요. 예제는 가벼운 Flash Lite 모델을 쓰고, 한 번 실행할 때 모델 호출이 몇 번 안 되게 만들었어요.
> ⚠️ API 키는 코드에 직접 적지 말고 환경변수로만 넣어 주세요. `.env` 파일은 `.gitignore`에 들어 있어요.

## 참고 자료

내용은 원 논문과 공식 문서를 근거로 했어요. 편별 자료는 각 영상 설명란에 정리해 둬요.

- Yao 외, *ReAct: Synergizing Reasoning and Acting in Language Models* (2022) — https://arxiv.org/abs/2210.03629
- Anthropic, *Building effective agents* (2024) — https://www.anthropic.com/engineering/building-effective-agents
- Gemini API 함수 호출 문서 — https://ai.google.dev/gemini-api/docs/function-calling

강의 주제 구성은 [Hello-Agents (Datawhale)](https://github.com/datawhalechina/hello-agents)를 참고했어요. 이 저장소의 예제와 코드는 강의를 위해 새로 작성했어요.

## 라이선스

코드는 [MIT 라이선스](LICENSE)로 자유롭게 쓰셔도 돼요.
