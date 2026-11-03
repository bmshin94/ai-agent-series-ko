# 기억하는 점심 에이전트 — 1편 lunch_agent.py에 '기억 도구' 2개만 더했어요
# 준비: pip install google-genai
#       환경변수 GOOGLE_API_KEY (또는 GEMINI_API_KEY)에 Gemini API 키 넣기
# 실행: python memory_agent.py            (오늘 날짜로)
#       python memory_agent.py 2026-10-21 (실습용: 날짜를 바꿔서 '어제'를 만들기)
import json
import sys
from datetime import date, timedelta
from pathlib import Path

from google import genai
from google.genai import types

client = genai.Client()
MODEL = "gemini-flash-lite-latest"
MAX_STEPS = 5
TODAY = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
MEMORY_FILE = Path("lunch_history.json")  # 장기 기억: 그냥 파일 하나


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


# ── 새 도구 2개: 기억 읽기·쓰기 ──
def recall_meals(days: int) -> list[dict]:
    """최근 며칠 동안 점심을 먹은 날짜와 식당 기록을 돌려준다."""
    if not MEMORY_FILE.exists():
        return []
    meals = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    since = str(TODAY - timedelta(days=days))
    return [m for m in meals if since <= m["date"] < str(TODAY)]


def save_meal(restaurant: str) -> str:
    """오늘 점심으로 정한 식당을 기억 파일에 적어 둔다."""
    meals = json.loads(MEMORY_FILE.read_text(encoding="utf-8")) if MEMORY_FILE.exists() else []
    meals.append({"date": str(TODAY), "restaurant": restaurant})
    MEMORY_FILE.write_text(json.dumps(meals, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"{TODAY} 점심: {restaurant} 기록 완료"


TOOLS = {f.__name__: f for f in [list_restaurants, check_wallet, calculate, recall_meals, save_meal]}

# 기억을 언제 쓸지는 지시문으로 알려 주고, 실제로 꺼내고 적는 건 모델이 도구로 정해요
RULES = "추천하기 전에 최근 먹은 곳을 확인해서 겹치지 않게 골라. 최종 결정한 식당은 꼭 기록해 둬."


# ── 에이전트 루프: 1편과 똑같아요 (모델 호출 수만 세어 봐요) ──
def run_agent(goal: str) -> str:
    history = [types.Content(role="user", parts=[types.Part(text=goal)])]
    config = types.GenerateContentConfig(
        system_instruction=RULES,
        tools=list(TOOLS.values()),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    for step in range(1, MAX_STEPS + 1):
        response = client.models.generate_content(model=MODEL, contents=history, config=config)
        history.append(response.candidates[0].content)

        if not response.function_calls:
            print(f"(모델 호출 {step}번)")
            return response.text

        for call in response.function_calls:
            result = TOOLS[call.name](**call.args)
            print(f"[{step}단계] {call.name}({dict(call.args)}) → {result}")
            history.append(types.Content(role="user", parts=[
                types.Part.from_function_response(name=call.name, response={"result": result})
            ]))

    return f"{MAX_STEPS}단계 안에 끝내지 못해서 멈췄어요."


if __name__ == "__main__":
    print(f"=== {TODAY} ===")
    print(run_agent("지갑에 있는 돈으로 둘이 같이 먹을 점심 메뉴 골라줘. 이유도 알려줘."))
