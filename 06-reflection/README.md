# 6편: 스스로 검토하는 에이전트 — 반성(Reflection)

5편의 일주일 점심 계획을 **만들기 → 검토 → 고치기** 루프로 다듬어 봐요. 핵심 질문은 하나예요. **검토는 누가 해야 할까?**

규칙 4개 (가능한 계획은 2,520가지 순서 중 144개뿐):
1. 월~금 합계 38,000원 이하
2. 같은 식당은 한 번만
3. 국물 요리(국밥·쌀국수·라멘)는 이틀 연속 금지
4. 5일 평점 평균 4.2 이상

| 파일 | 내용 |
|---|---|
| `lunch_rules.py` | 식당 7곳(가격·평점·국물), 규칙, 코드 검사기 `check_plan`, 얼마나 모자란지 알려 주는 `numbers`, 모델 호출 간격 조절(무료 한도) |
| `reflect.py` | 반성 루프 `draft` → 검토 → `revise`, 고치기 최대 `MAX_ROUNDS = 3`번. 검토 방식 5가지(A 한 번에 · B 기준 없이 '더 좋게' · C 모델이 스스로 검토 · D 코드가 검토 · E 코드가 검토 + 숫자) |
| `compare.py` | 방식별로 같은 과제를 N번씩 (`python compare.py` = A~D 5번씩, `python compare.py 5 E` = E만 5번) |
| `pilot.py` | 예비 실험 (A~D 3번씩) |
| `실행기록_*.txt` | 2026-11-16에 실제로 실행한 결과 (모델: gemini-flash-lite-latest) |

## 실행

```bash
cd 06-reflection
python reflect.py          # 방식 A~D 한 번씩
python compare.py          # A~D 5번씩 (호출 사이 4.2초씩 쉬어서 몇 분 걸려요)
python compare.py 5 E      # 코드가 검토 + 숫자, 5번
```

준비: `pip install google-genai`, 환경변수 `GOOGLE_API_KEY`에 Gemini API 키

> ⚠️ 무료 한도는 모델마다 달라요. 제가 실행할 때(2026-11) Flash Lite 모델은 무료로 **1분에 15번**까지라 `lunch_rules.py`의 `generate`가 호출 사이를 4.2초씩 띄워요.
> 모델의 답은 실행할 때마다 달라요. 방식별 5번씩의 작은 실험이라, 결과가 영상과 똑같지 않아도 이상한 게 아니에요.

## 실험 결과 (실행 기록 참고)

방식별 5번, 고치기 최대 3번 (`실행기록_비교.txt`, `실행기록_숫자안내.txt`)

| 방식 | 초안 통과 | 최종 통과 | 모델 호출 평균 |
|---|---|---|---|
| A 한 번에 | 1/5 | 1/5 | 1.0번 |
| B 기준 없이 "더 좋게 고쳐 줘" | 3/5 | **2/5** (맞던 계획을 고치다 망침) | 2.0번 |
| C 모델이 스스로 검토 | 1/5 | **1/5** | 3.2번 |
| D 코드가 검토 | 1/5 | 3/5 (2번은 3번 다 고쳐도 실패) | 2.8번 |
| E 코드가 검토 + 숫자 | 2/5 | **5/5** | 2.0번 |

- 모델 검토 판정 8번: 맞음 3 · 문제를 놓침 4(전부 평점 평균 위반) · 괜찮은 계획을 문제 있다고 함 1
- 예비 실험(`실행기록_예비실험.txt`)에서는 모델 검토가 설명엔 "모든 규칙을 만족"이라고 쓰고 판정은 `ok: false`로 내는 일이 3번 연속 있었어요
- 코드 검토는 문제를 한 번도 틀리지 않고 찾았지만, **고치는 건 여전히 모델**이에요. 무엇을 어겼는지에 더해 **얼마나 모자란지**(평점 합 0.3 모자람, 예산 2,200원 남음)를 알려 주자 다 통과했어요

## 반성 루프의 세 가지 열쇠
1. 검토관은 정확하게 — 계산할 수 있는 건 코드가 검토한다
2. 피드백은 구체적으로 — 무엇을 어겼는지에 더해 얼마나 모자란지까지
3. 반복은 짧게 — 횟수 제한을 두고, 못 고치면 사람에게 넘긴다

## 직접 해보기
1. `MAX_ROUNDS`를 1로 줄이거나 5로 늘려서, 통과 횟수와 호출 수가 어떻게 바뀌는지 세어 보세요
2. `numbers()`에 국물 요리가 어느 요일에 있는지도 알려 줘 보세요

## 참고
- Madaan 외, [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651) (NeurIPS 2023) — 7개 과제 평균 약 20% 향상, 수학은 92.9 → 93.1
- Shinn 외, [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) (NeurIPS 2023) — 스스로 만든 테스트 실행 결과로 반성, HumanEval 91%
- Huang 외, [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798) (Google DeepMind 외, 2023) — 바깥 피드백 없이 스스로 고치면 GPT-3.5 75.8% → 38.1%
- Stechly·Valmeekam·Kambhampati, [On the Self-Verification Limitations of LLMs on Reasoning and Planning Tasks](https://arxiv.org/abs/2402.08115) (2024) — 그래프 색칠: 그냥 16% / 스스로 검토 2% / 정확한 검사기 38%
- Gou 외, [CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing](https://arxiv.org/abs/2305.11738) (ICLR 2024)
- Kamoi 외, [When Can LLMs Actually Correct Their Own Mistakes?](https://arxiv.org/abs/2406.01297) (TACL 2024)

강의 주제 구성은 [Hello-Agents (Datawhale)](https://github.com/datawhalechina/hello-agents)를 참고했어요. 예제와 코드는 이 영상을 위해 새로 작성했어요.
