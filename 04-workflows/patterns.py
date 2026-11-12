# 4편: 워크플로 패턴 5가지 — 전부 점심 문제로 (프레임워크 없이 파이썬 + Gemini만)
# 실행: python patterns.py chain | route | parallel | orchestrator | evaluator
# 모든 패턴에서 '다음에 무엇을 할지'는 코드가 정해요. 모델은 정해진 칸 안에서 글을 쓰거나 고르기만 해요
import json, sys, time
from concurrent.futures import ThreadPoolExecutor

from google.genai import types

from lunch_tools import MENU_TAGS, MODEL, WALK_MINUTES, client, list_restaurants

CALLS = 0


def ask(prompt: str, as_json: bool = False) -> str:
    """모델 한 번 부르기 (호출 수를 세요)"""
    global CALLS
    CALLS += 1
    config = types.GenerateContentConfig(response_mime_type="application/json") if as_json else None
    return client.models.generate_content(model=MODEL, contents=prompt, config=config).text.strip()


PRICE = {r["name"]: r["price"] for r in list_restaurants()}
TABLE = "\n".join(f"- {n}: 1인 {PRICE[n]}원, 걸어서 {WALK_MINUTES[n]}분, 메뉴 {'·'.join(MENU_TAGS[n])}" for n in PRICE)


# ① 프롬프트 체이닝: 앞 단계의 결과가 다음 단계의 입력. 사이사이 코드가 검사(관문)
def chain():
    draft = ask("분식나라(둘이 9,600원, 걸어서 6분)를 점심으로 추천하는 문구를 세 문장으로 써 줘.")
    print(f"[1단계 추천 문구]\n{draft}")
    if "분식나라" not in draft:                       # 관문: 식당 이름이 빠졌으면 여기서 멈춤
        return print("관문 통과 못 함: 식당 이름이 없어요")
    short = ask(f"다음 글을 팀 메신저에 올릴 한 줄(40자 이내)로 줄여 줘. 이모지 하나.\n\n{draft}")
    print(f"[2단계 한 줄 요약] {short} ({len(short)}자)")


# ② 라우팅: 요청을 먼저 분류하고, 분류마다 다른 처리로 보냄
HANDLERS = {
    "가까운 곳": lambda: min(PRICE, key=lambda n: WALK_MINUTES[n]),
    "특별한 날": lambda: max(PRICE, key=lambda n: PRICE[n]),
    "아끼기": lambda: min(PRICE, key=lambda n: PRICE[n]),
}


def route():
    for req in ["비 와서 멀리 못 가겠어. 제일 가까운 데로", "월급날이다! 오늘은 좀 비싸도 맛있는 거", "이번 달 너무 쪼들려…"]:
        label = ask(f"점심 요청을 다음 중 하나로만 분류해. 답은 분류 이름만: {', '.join(HANDLERS)}\n요청: {req}")
        pick = HANDLERS.get(label, HANDLERS["아끼기"])()
        print(f"요청: {req}\n  → 분류: {label} → {pick}")


# ③ 병렬화: 서로 상관없는 일은 동시에
def intro(name):
    return ask(f"{name}(1인 {PRICE[name]}원, 메뉴 {'·'.join(MENU_TAGS[name])})를 점심 후보로 소개하는 한 문장.")


def parallel():
    names = ["분식나라", "국밥집", "제육볶음집"]
    t = time.perf_counter()
    for n in names:
        intro(n)
    one_by_one = time.perf_counter() - t
    t = time.perf_counter()
    with ThreadPoolExecutor() as pool:
        results = list(pool.map(intro, names))
    together = time.perf_counter() - t
    for n, r in zip(names, results):
        print(f"- {n}: {r}")
    print(f"하나씩: {one_by_one:.1f}초 / 동시에: {together:.1f}초")


# ④ 오케스트레이터-워커: 어떤 하위 작업이 필요한지는 '팀장 모델'이 그때그때 정하고, 워커들이 나눠서 처리
def orchestrator():
    goal = "팀 4명 점심. 민수는 매운 거 못 먹고, 지영이는 국물을 원하고, 1인 1만 원 이하, 걸어서 10분 안."
    plan = json.loads(ask(f"너는 팀장이야. 목표를 위해 필요한 하위 작업을 2~4개로 나눠. "
                          f'JSON 배열로만: [{{"task": "..."}}]\n목표: {goal}\n식당 정보:\n{TABLE}', as_json=True))
    print("[팀장이 나눈 일]")
    results = []
    for i, p in enumerate(plan, 1):
        print(f"  {i}. {p['task']}")
        results.append(ask(f"식당 정보:\n{TABLE}\n\n다음 일만 처리하고 한두 문장으로 답해: {p['task']}"))
    final = ask(f"목표: {goal}\n워커들의 결과:\n" + "\n".join(f"- {r}" for r in results) +
                "\n\n결과를 모아 식당 하나를 고르고 이유를 두 문장으로. 마지막 줄은 '최종 선택: 식당이름'.")
    print(f"[팀장의 결론]\n{final}")


# ⑤ 평가자-최적화: 한 모델이 쓰고, 다른 모델(검사관)이 기준대로 검사해서 통과할 때까지 고쳐 씀
RULES = "① 가격(둘이 9,600원)과 거리(걸어서 6분)가 들어 있다 ② 두 문장 이하 ③ '최고', '환상적' 같은 과장 표현이 없다"


def evaluator():
    text = ask("분식나라를 점심으로 추천하는 문구를 써 줘. 둘이 9,600원, 걸어서 6분.")
    for round_ in range(1, 4):
        print(f"[{round_}번째 글] {text}")
        verdict = json.loads(ask(f"검사 기준: {RULES}\n글: {text}\n"
                                 f'기준을 모두 지키면 pass를 true로. JSON으로만: {{"pass": true/false, "feedback": "..."}}', as_json=True))
        print(f"  검사관: {'통과' if verdict['pass'] else '다시'} — {verdict['feedback']}")
        if verdict["pass"]:
            break
        text = ask(f"다음 피드백대로 고쳐 써. 글만 답해.\n피드백: {verdict['feedback']}\n기준: {RULES}\n글: {text}")


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "chain"
    {"chain": chain, "route": route, "parallel": parallel, "orchestrator": orchestrator, "evaluator": evaluator}[name]()
    print(f"(모델 호출 {CALLS}번)")
