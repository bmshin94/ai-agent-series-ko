# 3편 측정: 나쁜 도구(v1)와 좋은 도구(v3)를 같은 질문으로 5번씩 돌려 정답(분식나라) 횟수를 센다
# 실행: python experiment.py
import contextlib, io, re

from walk_agent import GOAL, VERSIONS, run_agent

ANSWER = "분식나라"  # 둘이 9,600원(예산 1만 원 안) + 걸어서 6분. 김밥천국은 더 싸지만 12분
RUNS = 5

summary = {}
for version in ("v1", "v3"):
    ok, walked, calls = 0, 0, 0
    for i in range(1, RUNS + 1):
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                final = run_agent(GOAL, VERSIONS[version])
        except Exception as e:  # 도구가 예외를 던지면 루프 전체가 멈춤
            final = f"(실행 중단: {type(e).__name__}: {e})"
        log = buf.getvalue()
        pick = re.search(r"최종 선택\s*[:：]\s*\**\s*([^\s*\n]+)", final)
        pick = pick.group(1) if pick else "(형식 없음)"
        used_walk = "walk(" in log or "get_walking_minutes(" in log
        n_calls = int(m.group(1)) if (m := re.search(r"모델 호출 (\d+)번", log)) else 0
        ok += pick.startswith(ANSWER)
        walked += used_walk
        calls += n_calls
        print(f"[{version} {i}회] 걸어서 몇 분 도구 사용: {'예' if used_walk else '아니오'} / 최종 선택: {pick} / 모델 호출 {n_calls}번")
    summary[version] = (ok, walked, calls)

print()
for version, (ok, walked, calls) in summary.items():
    print(f"{version}: 정답 {ok}/{RUNS} · 도구 사용 {walked}/{RUNS} · 모델 호출 합계 {calls}번")
