# 4편: 1~3편 점심 에이전트의 도구들 (3편 walk_agent.py v3와 같음) + 메뉴 종류 도구 하나
from google import genai

client = genai.Client()
MODEL = "gemini-flash-lite-latest"

WALK_MINUTES = {"김밥천국": 12, "분식나라": 6, "제육볶음집": 3, "국밥집": 8, "라멘집": 5}
MENU_TAGS = {"김밥천국": ["분식"], "분식나라": ["분식", "라면"], "제육볶음집": ["밥"], "국밥집": ["국물", "밥"], "라멘집": ["국물", "면"]}


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


def get_walking_minutes(restaurant_name: str) -> int:
    """회사에서 식당까지 걸어서 몇 분 걸리는지 돌려준다.
    거리 조건(예: 걸어서 10분 안)이 있으면 후보 식당마다 확인한다.
    restaurant_name에는 list_restaurants가 돌려준 name을 그대로 넣는다. 예: '분식나라'"""
    if restaurant_name not in WALK_MINUTES:
        return f"'{restaurant_name}'은(는) 모르는 식당이에요. 다음 이름 중 하나를 그대로 넣어 주세요: {', '.join(WALK_MINUTES)}"
    return WALK_MINUTES[restaurant_name]


def get_menu_tags(restaurant_name: str) -> list[str]:
    """식당의 메뉴 종류(예: 국물, 밥, 면, 분식)를 돌려준다.
    메뉴 조건(예: 국물 있는 곳)이 있으면 후보 식당마다 확인한다.
    restaurant_name에는 list_restaurants가 돌려준 name을 그대로 넣는다."""
    if restaurant_name not in MENU_TAGS:
        return f"'{restaurant_name}'은(는) 모르는 식당이에요. 다음 이름 중 하나를 그대로 넣어 주세요: {', '.join(MENU_TAGS)}"
    return MENU_TAGS[restaurant_name]


TOOLS = [list_restaurants, check_wallet, calculate, get_walking_minutes]
