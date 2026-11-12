# 4편 측정: 같은 점심 문제를 에이전트와 워크플로로 각각 5번 — 정답 횟수·모델 호출 수·토큰·걸린 시간
# 실행: python compare.py
# ※ 무료 한도(분당 15번)에 걸리지 않게 실행 사이에 20초씩 쉬어요. 걸린 시간에는 쉬는 시간이 들어가지 않아요
import contextlib, io, re, time

from lunch_agent import GOAL, run_agent
from lunch_workflow import run_workflow

ANSWER = "분식나라"  # 둘이 9,600원(예산 1만 원 안) + 걸어서 6분. 김밥천국은 더 싸지만 12분
RUNS = 5
REST = 20

rows = {"에이전트": [], "워크플로": []}
for name, fn in (("에이전트", lambda: run_agent(GOAL, verbose=False)), ("워크플로", lambda: run_workflow(verbose=False))):
    for i in range(1, RUNS + 1):
        start = time.perf_counter()
        with contextlib.redirect_stdout(io.StringIO()):
            r = fn()
        sec = time.perf_counter() - start
        m = re.search(r"최종 선택\s*[:：]\s*\**\s*([^\s*\n]+)", r["answer"])
        pick = m.group(1) if m else "(형식 없음)"
        rows[name].append((pick.startswith(ANSWER), r["model_calls"], r["tokens"], sec))
        print(f"[{name} {i}회] 최종 선택: {pick} / 모델 호출 {r['model_calls']}번 / 토큰 {r['tokens']}개 / {sec:.1f}초", flush=True)
        time.sleep(REST)

print()
for name, rs in rows.items():
    ok = sum(r[0] for r in rs)
    calls = sum(r[1] for r in rs)
    tokens = sum(r[2] for r in rs)
    secs = sum(r[3] for r in rs)
    print(f"{name}: 정답 {ok}/{RUNS} · 모델 호출 합계 {calls}번(평균 {calls / RUNS:.1f}) · 토큰 합계 {tokens}개(평균 {tokens / RUNS:.0f}) · 평균 {secs / RUNS:.1f}초")
