# 6편: 반성(Reflection) — 만들기 → 검토하기 → 고치기
# 방식 A 한 번에: 계획표를 한 번만 받음
# 방식 B 기준 없이 다시 보기: "다시 검토하고 더 좋게 고쳐 줘"만 말함
# 방식 C 모델이 스스로 검토: 규칙 4개를 주고 같은 모델에게 검토를 맡김 (괜찮다고 하면 멈춤)
# 방식 D 코드가 검토: lunch_rules.check_plan이 계산으로 찾은 문제를 모델에게 알려 줌
# 방식 E 코드가 검토 + 숫자: D에 더해 합계·평점 합이 기준에서 얼마나 떨어져 있는지도 알려 줌
# 실행: python reflect.py
import json

from lunch_rules import RESTAURANTS, RULES, check_plan, generate, numbers, parse, short

MAX_ROUNDS = 3  # 반성에도 횟수 제한 (고치기 최대 3번)

TASK = (f"이번 주 점심 계획표를 세워 줘. 규칙: {RULES}\n"
        f"식당 목록: {json.dumps(RESTAURANTS, ensure_ascii=False)}\n"
        'JSON으로만 답해: {"월": "식당", "화": "식당", "수": "식당", "목": "식당", "금": "식당"}')


def draft():
    return parse(generate(TASK))


def revise(plan, feedback: str):
    prompt = f"{TASK}\n\n방금 세운 계획: {json.dumps(plan, ensure_ascii=False)}\n검토 의견: {feedback}\n고친 계획표를 JSON으로만 답해."
    return parse(generate(prompt))


def model_review(plan) -> tuple[bool, list[str]]:
    """같은 모델에게 규칙 4개로 검토를 맡김"""
    prompt = (f"아래 점심 계획표가 규칙을 모두 지키는지 검토해. 이 계획은 맞을 수도, 틀릴 수도 있어. 규칙마다 직접 계산해서 확인해.\n"
              f"규칙: {RULES}\n식당 목록: {json.dumps(RESTAURANTS, ensure_ascii=False)}\n"
              f"계획: {json.dumps(plan, ensure_ascii=False)}\n"
              'JSON으로만 답해: {"ok": true 또는 false, "problems": ["어긴 규칙과 이유"]}')
    r = parse(generate(prompt))
    if not isinstance(r, dict):
        return False, [f"검토 답 형식이 이상함: {str(r)[:40]}"]
    return bool(r.get("ok")), list(r.get("problems") or [])


def run(method: str, verbose=True) -> dict:
    plan, calls = draft(), 1
    truth = check_plan(plan)
    log = [f"[초안] {short(plan)} → 코드 검사: {'통과' if not truth else truth}"]
    first_ok = not truth
    judge = []  # 모델 검토 판정: 맞음 / 놓침 / 헛짚음
    worse = 0  # 고친 뒤 문제가 더 많아진 횟수
    for rnd in range(1, MAX_ROUNDS + 1):
        if method == "A":
            break
        if method == "B":
            feedback = "계획을 다시 검토하고 더 좋게 고쳐 줘."
        elif method == "C":
            ok, problems = model_review(plan)
            calls += 1
            verdict = "맞음" if (ok == (not truth)) else ("틀림: 문제를 놓침" if ok else "틀림: 괜찮은 계획을 문제 있다고 함")
            judge.append("맞음" if verdict == "맞음" else ("놓침" if ok else "헛짚음"))
            log.append(f"  [검토 {rnd}] 모델: {'괜찮음' if ok else problems} (모델 판정 {verdict})")
            if ok:
                break
            feedback = "; ".join(problems)
        else:  # D, E
            if not truth:
                break
            feedback = "; ".join(truth)
            if method == "E" and isinstance(plan, dict) and not truth[0].startswith(("형식", "모르는")):
                feedback += f" / {numbers(plan)}"
            log.append(f"  [검토 {rnd}] 코드: {feedback}")
        before = len(truth)
        plan = revise(plan, feedback)
        calls += 1
        truth = check_plan(plan)
        worse += len(truth) > before
        log.append(f"  [고침 {rnd}] {short(plan)} → 코드 검사: {'통과' if not truth else truth}")
        if method == "B" and rnd == 1:
            break  # 기준 없이 다시 보기는 한 번만
    if verbose:
        print("\n".join(log), flush=True)
    return {"method": method, "first_ok": first_ok, "final_ok": not truth, "calls": calls, "plan": plan, "judge": judge, "worse": worse}


if __name__ == "__main__":
    for m in "ABCD":
        print(f"\n===== 방식 {m} =====")
        r = run(m)
        print(f"→ 최종 {'통과' if r['final_ok'] else '실패'}, 모델 호출 {r['calls']}번")
