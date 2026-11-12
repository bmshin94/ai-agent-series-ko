# 3편: '걸어서 몇 분' 도구 — 같은 도구를 세 가지 버전으로 (1편 점심 에이전트 + 도구 하나)
# 준비: pip install google-genai / 환경변수 GOOGLE_API_KEY
# 실행: python walk_agent.py v1        (나쁜 도구)
#       python walk_agent.py v3        (좋은 설명 + 친절한 실패 메시지)
#       python walk_agent.py v2 "김밥 천국까지 걸어서 몇 분이야?"   (질문을 바꿔서 실행)
import sys

from google import genai
from google.genai import types

client = genai.Client()
MODEL = "gemini-flash-lite-latest"
MAX_STEPS = 6
GOAL = ("지갑에 있는 돈으로 둘이 같이 먹을 수 있고, 회사에서 걸어서 10분 안에 갈 수 있는 점심 메뉴 골라줘. "
        "마지막 줄은 '최종 선택: 식당이름'으로 끝내 줘.")

WALK_MINUTES = {"김밥천국": 12, "분식나라": 6, "제육볶음집": 3, "국밥집": 8, "라멘집": 5}


# ── 1편 도구 3개 (그대로) ──
def list_restaurants() -> list[dict]:
    """회사 근처 식당 이름과 1인분 가격(원) 목록을 돌려준다."""
    return [
        {"name": "김밥천국", "price": 4500},
        {"name": "분식나라", "price": 4800},
        {"name": "제육볶음집", "price": 8000},
        {"name": "국밥집", "price": 9000},
        {"name": "라멘집", "price": 11000},
    ]


def check_wallet() -> int:
    """지갑에 남은 돈(원)을 돌려준다."""
    return 10000


def calculate(expression: str) -> float:
    """사칙연산 수식을 계산한다. 예: '4500 * 2'"""
    if not set(expression) <= set("0123456789+-*/(). "):
        return "숫자와 + - * / ( ) 만 쓸 수 있어요"
    return eval(expression)


# ── v1: 나쁜 도구 — 이름도, 설명도, 매개변수도 모호해요 ──
def walk(r: str) -> int:
    """시간"""
    return WALK_MINUTES[r]


# ── v2: 좋은 설명 — 무엇을, 언제, 어떤 값으로 ──
def get_walking_minutes(restaurant_name: str) -> int:
    """회사에서 식당까지 걸어서 몇 분 걸리는지 돌려준다.
    거리 조건(예: 걸어서 10분 안)이 있으면 후보 식당마다 확인한다.
    restaurant_name에는 list_restaurants가 돌려준 name을 그대로 넣는다. 예: '분식나라'"""
    return WALK_MINUTES[restaurant_name]


# ── v3: v2 + 실패하면 고칠 방법을 알려주는 메시지 ──
def get_walking_minutes_v3(restaurant_name: str) -> int:
    """회사에서 식당까지 걸어서 몇 분 걸리는지 돌려준다.
    거리 조건(예: 걸어서 10분 안)이 있으면 후보 식당마다 확인한다.
    restaurant_name에는 list_restaurants가 돌려준 name을 그대로 넣는다. 예: '분식나라'"""
    if restaurant_name not in WALK_MINUTES:
        return f"'{restaurant_name}'은(는) 모르는 식당이에요. 다음 이름 중 하나를 그대로 넣어 주세요: {', '.join(WALK_MINUTES)}"
    return WALK_MINUTES[restaurant_name]


get_walking_minutes_v3.__name__ = "get_walking_minutes"  # 모델에게 보이는 이름은 v2와 같게

BASE = [list_restaurants, check_wallet, calculate]
VERSIONS = {"v1": BASE + [walk], "v2": BASE + [get_walking_minutes], "v3": BASE + [get_walking_minutes_v3]}


# ── 에이전트 루프: 1편과 똑같아요 ──
def run_agent(goal: str, tool_list: list) -> str:
    tools = {f.__name__: f for f in tool_list}
    history = [types.Content(role="user", parts=[types.Part(text=goal)])]
    config = types.GenerateContentConfig(
        tools=tool_list,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    for step in range(1, MAX_STEPS + 1):
        response = client.models.generate_content(model=MODEL, contents=history, config=config)
        history.append(response.candidates[0].content)

        if not response.function_calls:
            print(f"(모델 호출 {step}번)")
            return response.text

        for call in response.function_calls:
            result = tools[call.name](**call.args)
            print(f"[{step}단계] {call.name}({dict(call.args)}) → {result}")
            history.append(types.Content(role="user", parts=[
                types.Part.from_function_response(name=call.name, response={"result": result})
            ]))

    return f"{MAX_STEPS}단계 안에 끝내지 못해서 멈췄어요."


if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "v3"
    goal = sys.argv[2] if len(sys.argv) > 2 else GOAL
    print(f"=== 도구 {version} ===")
    print(run_agent(goal, VERSIONS[version]))
