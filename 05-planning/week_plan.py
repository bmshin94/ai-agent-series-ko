# 5편: 방식 B — 계획 먼저 (계획표를 먼저 세우고 → 코드가 검사 → 통과하면 하루씩 실행 → 틀어지면 남은 날만 다시 계획)
# 실행: python week_plan.py
import json
from itertools import permutations

from google.genai import types

from week_tools import DAYS, PRICE, RESTAURANTS, Week, generate

MAX_PLANS = 3


def check_plan(plan, days: list[str], week: Week, closed: set[str] = frozenset()) -> list[str]:
    """계획표 검사는 코드가 해요 (모델에게 맡기지 않음)"""
    if not isinstance(plan, dict) or any(d not in plan for d in days):
        return [f"형식이 달라요: {'·'.join(days)}요일을 열쇠로 한 표가 아니에요 — 받은 값: {str(plan)[:60]}"]
    names = [plan[d] for d in days]
    problems = []
    if any(n not in PRICE for n in names):
        return [f"모르는 식당이 있어요: {[n for n in names if n not in PRICE]}"]
    if any(n in closed for n in names):
        problems.append(f"문 닫은 식당이 있어요: {[n for n in names if n in closed]}")
    total = week.spent + sum(week.cost(d, plan[d]) for d in days)
    if total > week.budget:
        problems.append(f"합계 {total}원 — 예산 {week.budget}원을 {total - week.budget}원 넘어요")
    already = [n for _, n in week.visited]
    if len(set(names)) != len(names) or any(n in already for n in names):
        problems.append(f"같은 식당이 두 번 있어요: {[n for n in set(names + already) if (names + already).count(n) > 1]}")
    return problems


def count_possible(week: Week, days: list[str], closed: set[str] = frozenset()) -> int:
    """남은 조건으로 가능한 계획이 몇 개인지 코드가 전부 세어 봐요 (식당 7곳이라 금방 끝남)"""
    already = {n for _, n in week.visited}
    cand = [n for n in PRICE if n not in already and n not in closed]
    left = week.budget - week.spent
    return sum(1 for c in permutations(cand, len(days)) if sum(week.cost(d, n) for d, n in zip(days, c)) <= left)


def make_plan(week: Week, days: list[str], closed: set[str] = frozenset(), verbose=True) -> tuple[dict | None, int]:
    """검사를 통과한 계획표만 돌려줘요. MAX_PLANS번 안에 못 세우면 None (틀린 계획은 실행하지 않음)"""
    possible = count_possible(week, days, closed)
    if possible == 0:  # 가능성 검사: 답이 없는 문제는 모델에게 묻지 않음
        if verbose:
            print(f"[가능성 검사] 남은 예산 {week.budget - week.spent}원으로 가능한 계획 0개 → 모델을 부르지 않고 사람에게 넘김", flush=True)
        return None, 0
    if verbose and week.visited:
        print(f"[가능성 검사] 가능한 계획 {possible}개 → 모델에게 다시 계획 요청", flush=True)
    done = f" 이미 먹은 곳: {[n for _, n in week.visited]}, 이미 쓴 돈: {week.spent}원." if week.visited else ""
    shut = f" 문 닫은 곳: {sorted(closed)}." if closed else ""
    keys = ", ".join(f'"{d}": "식당"' for d in days)
    prompt = (f"점심 계획표를 세워 줘. 규칙: {week.rules()}{done}{shut} 남은 요일: {'·'.join(days)}.\n"
              f"식당 목록: {json.dumps(RESTAURANTS, ensure_ascii=False)}\nJSON으로만 답해: {{{keys}}}")
    config = types.GenerateContentConfig(response_mime_type="application/json")
    calls = 0
    for attempt in range(1, MAX_PLANS + 1):
        plan = json.loads(generate(contents=prompt, config=config).text)
        calls += 1
        problems = check_plan(plan, days, week, closed)
        if verbose:
            print(f"[계획 {attempt}번째] {plan} → {'통과' if not problems else problems}", flush=True)
        if not problems:
            return plan, calls
        prompt += f"\n\n방금 계획은 이런 문제가 있었어: {problems}. 고쳐서 다시 JSON으로만 답해."
    if verbose:
        print(f"[계획 실패] {MAX_PLANS}번 안에 검사를 통과하지 못함 → 실행하지 않고 사람에게 넘김", flush=True)
    return None, calls


def run_week(budget=35000, guest_day=None, closed_on=None, verbose=True) -> dict:
    """closed_on=("수", None)이면 그날 계획한 식당이 문을 닫아서 남은 날만 다시 계획"""
    week = Week(budget, guest_day)
    plan, calls = make_plan(week, DAYS, verbose=verbose)
    replans, stopped = 0, plan is None
    for i, day in enumerate(DAYS):
        if stopped:
            break
        pick = plan[day]
        if closed_on and day == closed_on[0]:
            if verbose:
                print(f"[{day}] 계획은 {pick}인데… 오늘 휴무! 남은 날만 다시 계획", flush=True)
            plan_rest, c = make_plan(week, DAYS[i:], closed={pick}, verbose=verbose)
            calls += c
            replans += 1
            if plan_rest is None:
                stopped = True
                break
            plan.update(plan_rest)
            pick = plan[day]
        week.pay(day, pick)
        if verbose:
            print(f"[{day}] {pick} {week.cost(day, pick)}원 (누적 {week.spent}원)", flush=True)
    rep = week.report()
    rep.update({"model_calls": calls, "replans": replans, "stopped": stopped})
    return rep


if __name__ == "__main__":
    print(run_week())
