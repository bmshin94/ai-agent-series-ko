# 3편 추가 측정: 현장에서 자주 나오는 '나쁜 도구' 유형별로 5번씩 실행
# 1차 실험(experiment.py)에서 v1(walk, 설명 '시간')도 5/5 정답 → 이름과 질문만으로 짐작이 가능했음
# 실행: python experiment2.py
import contextlib, io, re

from walk_agent import BASE, GOAL, WALK_MINUTES, run_agent, get_walking_minutes, get_walking_minutes_v3

ANSWER, RUNS = "분식나라", 5


# 유형 A: 단위가 숨은 도구 — 지도 API처럼 '초'로 돌려주는데 설명엔 '시간'뿐
def walk(r: str) -> int:
    """시간"""
    return WALK_MINUTES[r] * 60


# 유형 A를 고친 버전 — 단위를 설명과 값에 모두 밝힘
def get_walking_minutes_unit(restaurant_name: str) -> int:
    """회사에서 식당까지 걸어서 몇 '분' 걸리는지 돌려준다 (단위: 분).
    restaurant_name에는 list_restaurants가 돌려준 name을 그대로 넣는다. 예: '분식나라'"""
    return WALK_MINUTES[restaurant_name]


get_walking_minutes_unit.__name__ = "get_walking_minutes"


# 유형 B: 이름·설명에 아무 단서가 없는 도구
def t(x: str) -> int:
    """시간"""
    return WALK_MINUTES[x]


def measure(label, tools, goal=GOAL):
    ok, used, crashed = 0, 0, 0
    for i in range(1, RUNS + 1):
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                final = run_agent(goal, tools)
        except Exception as e:
            final = f"(실행 중단: {type(e).__name__}: {e})"
            crashed += 1
        log = buf.getvalue()
        pick = re.search(r"최종 선택\s*[:：]\s*\**\s*([^\s*\n]+)", final)
        pick = pick.group(1) if pick else final.strip().splitlines()[-1][:40]
        calls = [l.split("]", 1)[1].strip()[:60] for l in log.splitlines() if l.startswith("[") and ("walk(" in l or "t({" in l or "get_walking" in l)]
        used += bool(calls)
        ok += pick.startswith(ANSWER)
        print(f"[{label} {i}회] 최종: {pick} / 걸음 도구 호출 예: {calls[0] if calls else '없음'}")
    print(f"→ {label}: 정답 {ok}/{RUNS} · 도구 사용 {used}/{RUNS} · 중단 {crashed}/{RUNS}\n")


if __name__ == "__main__":
    measure("A 초 단위·설명 '시간'", BASE + [walk])
    measure("A 고침: 단위 '분' 명시", BASE + [get_walking_minutes_unit])
    measure("B 이름 단서 없음 t(x)", BASE + [t])
    typo = "회사에서 '김밥 천국'까지 걸어서 몇 분 걸려?"
    measure("C v2 띄어쓰기 질문(실패 시 예외)", BASE + [get_walking_minutes], typo)
    measure("C v3 띄어쓰기 질문(실패 메시지)", BASE + [get_walking_minutes_v3], typo)
