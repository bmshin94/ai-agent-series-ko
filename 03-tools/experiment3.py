# 3편 측정 3: 일 단위로 묶은 도구 — 식당마다 걸어서 몇 분인지 하나씩 묻는 대신 '걸어서 N분 안 식당'을 한 번에
# 실행: python experiment3.py
import contextlib, io, re

from walk_agent import GOAL, WALK_MINUTES, check_wallet, calculate, list_restaurants, run_agent, get_walking_minutes_v3

RUNS = 3


def find_nearby_restaurants(max_minutes: int) -> list[dict]:
    """회사에서 걸어서 max_minutes분 안에 갈 수 있는 식당만 골라 이름, 1인분 가격(원), 걸어서 몇 분인지 돌려준다.
    거리 조건(예: 걸어서 10분 안)이 있으면 이 도구 하나로 후보를 찾는다."""
    return [{**r, "walk_minutes": WALK_MINUTES[r["name"]]} for r in list_restaurants() if WALK_MINUTES[r["name"]] <= max_minutes]


def measure(label, tools):
    for i in range(1, RUNS + 1):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            final = run_agent(GOAL, tools)
        log = buf.getvalue()
        tool_calls = [l for l in log.splitlines() if l.startswith("[")]
        n_model = int(m.group(1)) if (m := re.search(r"모델 호출 (\d+)번", log)) else 0
        pick = m.group(1) if (m := re.search(r"최종 선택\s*[:：]\s*\**\s*([^\s*\n]+)", final)) else "(형식 없음)"
        print(f"[{label} {i}회] 최종: {pick} / 도구 실행 {len(tool_calls)}번 / 모델 호출 {n_model}번")
        for l in tool_calls:
            print("   ", l[:110])


if __name__ == "__main__":
    measure("하나씩 묻기 (v3)", [list_restaurants, check_wallet, calculate, get_walking_minutes_v3])
    measure("한 번에 찾기", [find_nearby_restaurants, check_wallet, calculate])
