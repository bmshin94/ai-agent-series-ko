# 점심 결정 에이전트 — 파이썬으로 만드는 첫 AI 에이전트
# 준비: pip install google-genai
#       환경변수 GOOGLE_API_KEY (또는 GEMINI_API_KEY)에 Gemini API 키 넣기
from google import genai
from google.genai import types

client = genai.Client()  # 환경변수에서 API 키를 자동으로 읽어요
MODEL = "gemini-flash-lite-latest"
MAX_STEPS = 5  # 안전장치: 아무리 길어져도 5번까지만 반복


# ── 도구 3개: 에이전트의 '손발' (가짜 데이터라 무료로 똑같이 재현돼요) ──
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


TOOLS = {f.__name__: f for f in [list_restaurants, check_wallet, calculate]}


# ── 에이전트 루프: 생각 → 행동 → 관찰을 끝날 때까지 반복 ──
def run_agent(goal: str) -> str:
    history = [types.Content(role="user", parts=[types.Part(text=goal)])]
    config = types.GenerateContentConfig(
        tools=list(TOOLS.values()),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    )
    for step in range(1, MAX_STEPS + 1):
        # 1) 생각: 모델이 다음에 뭘 할지 정한다
        response = client.models.generate_content(
            model=MODEL, contents=history, config=config
        )
        history.append(response.candidates[0].content)

        if not response.function_calls:  # 도구 요청이 없다 = 결론이 났다
            return response.text

        for call in response.function_calls:
            # 2) 행동: 모델은 '요청'만 하고, 실제 실행은 우리 코드가 한다
            result = TOOLS[call.name](**call.args)
            print(f"[{step}단계] {call.name}({dict(call.args)}) → {result}")
            # 3) 관찰: 실행 결과를 대화 기록에 넣어서 모델에게 보여준다
            history.append(types.Content(role="user", parts=[
                types.Part.from_function_response(
                    name=call.name, response={"result": result}
                )
            ]))

    return f"{MAX_STEPS}단계 안에 끝내지 못해서 멈췄어요."


if __name__ == "__main__":
    print(run_agent("지갑에 있는 돈으로 둘이 같이 먹을 점심 메뉴 골라줘. 이유도 알려줘."))
