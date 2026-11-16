# 5편: 계획이 틀어지면? — 계획대로 가다가 수요일 식당이 문을 닫으면 남은 날만 다시 계획 (3번 실행)
# 실행: python replan.py          (예산 35,000원)
#       python replan.py 38000    (예산 38,000원 — 다시 계획할 여지가 있는 조건)
import sys

import week_plan

budget = int(sys.argv[1]) if len(sys.argv) > 1 else 35000
print(f"과제: 5일 합계 {budget}원 이하, 같은 식당 한 번만 / 수요일에 계획한 식당이 휴무", flush=True)
for i in range(1, 4):
    print(f"=== {i}회 ===", flush=True)
    r = week_plan.run_week(budget=budget, closed_on=("수", None))
    status = "계획 실패 → 남은 날은 사람에게" if r["stopped"] else ("조건 지킴" if r["ok"] else "조건 어김")
    print(f"→ {' → '.join(n for _, n in r['visited'])} / 합계 {r['spent']}원 / {status} / 다시 계획 {r['replans']}번 / 모델 호출 {r['model_calls']}번\n", flush=True)
