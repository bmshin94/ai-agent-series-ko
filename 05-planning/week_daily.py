# 5편: 방식 A — 하루씩 고르기 (매일 아침 새로 불러서 '오늘 점심'만 정함, 1~4편 루프 그대로)
# 실행: python week_daily.py
from google.genai import types

from week_tools import DAYS, Week, generate, list_restaurants

MAX_STEPS = 6


def run_day(day: str, week: Week) -> tuple[str, int]:
    def get_week_status() -> dict:
        """이번 주 지금까지 간 식당, 쓴 돈, 남은 예산(원), 오늘 포함 남은 날 수를 돌려준다."""
        return {"visited": [n for _, n in week.visited], "spent": week.spent, "remaining_budget": week.budget - week.spent,
                "days_left_including_today": 5 - len(week.visited)}

    tools = {"list_restaurants": list_restaurants, "get_week_status": get_week_status}
    goal = f"오늘은 {day}요일이야. 이번 주 점심 규칙: {week.rules()} 오늘 점심 한 곳만 골라줘. 마지막 줄은 '최종 선택: 식당이름'으로 끝내 줘."
    history = [types.Content(role="user", parts=[types.Part(text=goal)])]
    config = types.GenerateContentConfig(tools=list(tools.values()),
                                         automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
    calls = 0
    for _ in range(MAX_STEPS):
        r = generate(contents=history, config=config)
        calls += 1
        history.append(r.candidates[0].content)
        if not r.function_calls:
            text = r.text or ""
            pick = text.split("최종 선택:")[-1].strip().strip("*").split()[0] if "최종 선택:" in text else "?"
            return pick, calls
        for call in r.function_calls:
            result = tools[call.name](**call.args)
            history.append(types.Content(role="user", parts=[types.Part.from_function_response(name=call.name, response={"result": result})]))
    return "?", calls


def run_week(budget=35000, guest_day=None, verbose=True) -> dict:
    week, calls = Week(budget, guest_day), 0
    for day in DAYS:
        pick, c = run_day(day, week)
        calls += c
        week.pay(day, pick)
        if verbose:
            print(f"[{day}] {pick} {week.cost(day, pick)}원 (누적 {week.spent}원, 모델 호출 {c}번)", flush=True)
    rep = week.report()
    rep["model_calls"] = calls
    return rep


if __name__ == "__main__":
    print(run_week())
