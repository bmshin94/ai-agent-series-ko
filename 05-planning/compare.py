# 5편 측정: 하루씩(A) vs 계획 먼저(B), 같은 일주일 과제를 각 5번 — 조건 지킴·합계·평균 평점·모델 호출 수
# 실행: python compare.py            (기본: 5일 합계 35,000원, 같은 식당 한 번만)
#       python compare.py future     (금요일 손님 2인분, 예산 40,000원 — 미리 알 수 있는 미래 조건)
import contextlib, io, sys

import week_daily
import week_plan

RUNS = 5
mode = sys.argv[1] if len(sys.argv) > 1 else "basic"
kw = {"budget": 40000, "guest_day": "금"} if mode == "future" else {"budget": 35000}
print(f"과제: {'금요일 손님 2인분, ' if mode == 'future' else ''}5일 합계 {kw['budget']}원 이하, 같은 식당 한 번만, 이왕이면 평점 높게", flush=True)

summary = {}
for label, mod in (("하루씩", week_daily), ("계획 먼저", week_plan)):
    rows = []
    for i in range(1, RUNS + 1):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            r = mod.run_week(verbose=True, **kw)
        why = "".join([" 예산 초과" if r["over_budget"] else "", " 중복" if r["duplicate"] else "", f" 모르는 이름{r['unknown']}" if r["unknown"] else ""])
        if r.get("stopped"):
            print(f"[{label} {i}회] 계획 실패 → 실행 안 함 (사람에게 넘김) / 모델 호출 {r['model_calls']}번", flush=True)
        else:
            print(f"[{label} {i}회] {' → '.join(n for _, n in r['visited'])} / 합계 {r['spent']}원 / 조건 {'지킴' if r['ok'] else '어김:' + why}"
                  f" / 평균 평점 {r['rating']} / 모델 호출 {r['model_calls']}번", flush=True)
        for line in buf.getvalue().splitlines():
            print("    " + line, flush=True)
        rows.append(r)
    summary[label] = rows

print()
for label, rows in summary.items():
    ok = sum(r["ok"] for r in rows)
    stop = sum(bool(r.get("stopped")) for r in rows)
    bad = RUNS - ok - stop
    calls = sum(r["model_calls"] for r in rows)
    done = [r for r in rows if not r.get("stopped")]
    rating = sum(r["rating"] for r in done) / len(done) if done else 0
    print(f"{label}: 조건 지킴 {ok}/{RUNS} · 조건 어기고 실행 {bad}번 · 계획 실패로 멈춤 {stop}번 · 실행한 주 평균 평점 {rating:.2f} · 모델 호출 합계 {calls}번(평균 {calls / RUNS:.1f})")
