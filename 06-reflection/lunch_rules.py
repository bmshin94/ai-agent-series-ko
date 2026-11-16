# 6편: 일주일 점심 — 식당 데이터, 규칙, 코드 검사기, 모델 호출 (5편 식당 7곳 + '국물' 표시)
import json
import time

from google import genai
from google.genai import types

client = genai.Client()
MODEL = "gemini-flash-lite-latest"
DAYS = ["월", "화", "수", "목", "금"]

RESTAURANTS = [
    {"name": "김밥천국", "price": 4500, "rating": 3.5, "soup": False},
    {"name": "분식나라", "price": 4800, "rating": 3.8, "soup": False},
    {"name": "백반집", "price": 6000, "rating": 4.0, "soup": False},
    {"name": "제육볶음집", "price": 8000, "rating": 4.3, "soup": False},
    {"name": "국밥집", "price": 9000, "rating": 4.5, "soup": True},
    {"name": "쌀국수집", "price": 9500, "rating": 4.6, "soup": True},
    {"name": "라멘집", "price": 11000, "rating": 4.8, "soup": True},
]
INFO = {r["name"]: r for r in RESTAURANTS}

BUDGET = 38000
MIN_RATING = 4.2
RULES = (f"① 월~금 5일 점심 합계 {BUDGET:,}원 이하 "
         f"② 같은 식당은 한 주에 한 번만 "
         f"③ 국물 요리는 이틀 연속 금지 "
         f"④ 5일 평점 평균 {MIN_RATING} 이상")

_last = [0.0]


def generate(prompt: str, as_json=True) -> str:
    """모델 호출 (무료 한도: 분당 15번 → 호출 사이를 4.2초 이상 띄움)"""
    wait = 4.2 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()
    config = types.GenerateContentConfig(response_mime_type="application/json") if as_json else None
    return client.models.generate_content(model=MODEL, contents=prompt, config=config).text


def check_plan(plan) -> list[str]:
    """코드 검사기: 규칙 4개를 계산으로 확인해요. 문제가 없으면 빈 목록"""
    if not isinstance(plan, dict) or any(d not in plan for d in DAYS):
        return [f"형식이 달라요: 월~금을 열쇠로 한 표가 아니에요 — 받은 값: {str(plan)[:60]}"]
    names = [plan[d] for d in DAYS]
    if any(n not in INFO for n in names):
        return [f"모르는 식당이 있어요: {[n for n in names if n not in INFO]}"]
    problems = []
    total = sum(INFO[n]["price"] for n in names)
    if total > BUDGET:
        problems.append(f"① 합계 {total:,}원 — 예산을 {total - BUDGET:,}원 넘어요")
    dup = sorted({n for n in names if names.count(n) > 1})
    if dup:
        problems.append(f"② 같은 식당이 두 번: {dup}")
    for a, b in zip(DAYS, DAYS[1:]):
        if INFO[plan[a]]["soup"] and INFO[plan[b]]["soup"]:
            problems.append(f"③ {a}·{b} 이틀 연속 국물 ({plan[a]}, {plan[b]})")
    avg = sum(INFO[n]["rating"] for n in names) / 5
    if avg < MIN_RATING - 1e-9:
        problems.append(f"④ 평점 평균 {avg:.2f} — {MIN_RATING}보다 낮아요")
    return problems


def numbers(plan) -> str:
    """고칠 방향을 숫자로: 지금 합계·평점 합이 기준에서 얼마나 떨어져 있는지 (방식 E에서 사용)"""
    names = [plan[d] for d in DAYS]
    total = sum(INFO[n]["price"] for n in names)
    rsum = sum(INFO[n]["rating"] for n in names)
    need = MIN_RATING * 5
    money = f"지금 합계 {total:,}원 (예산까지 {abs(BUDGET - total):,}원 {'남음' if total <= BUDGET else '초과'})"
    rating = f"평점 합 {rsum:.1f} (평균 {MIN_RATING} 이상이 되려면 합이 {need:.1f} 이상 — 지금 {abs(need - rsum):.1f} {'모자람' if rsum < need - 1e-9 else '여유'})"
    return f"{money}, {rating}"


def parse(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def short(plan) -> str:
    """계획표를 한 줄로: 월 김밥천국 · 화 백반집 …"""
    if isinstance(plan, dict) and all(d in plan for d in DAYS):
        return " · ".join(f"{d} {plan[d]}" for d in DAYS)
    return str(plan)[:80]
