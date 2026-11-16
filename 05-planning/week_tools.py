# 5편: 일주일 점심 — 공용 데이터와 도구 (식당 7곳, 한 주 장부)
import time

from google import genai

client = genai.Client()
MODEL = "gemini-flash-lite-latest"
DAYS = ["월", "화", "수", "목", "금"]

RESTAURANTS = [
    {"name": "김밥천국", "price": 4500, "rating": 3.5},
    {"name": "분식나라", "price": 4800, "rating": 3.8},
    {"name": "백반집", "price": 6000, "rating": 4.0},
    {"name": "제육볶음집", "price": 8000, "rating": 4.3},
    {"name": "국밥집", "price": 9000, "rating": 4.5},
    {"name": "쌀국수집", "price": 9500, "rating": 4.6},
    {"name": "라멘집", "price": 11000, "rating": 4.8},
]
PRICE = {r["name"]: r["price"] for r in RESTAURANTS}
RATING = {r["name"]: r["rating"] for r in RESTAURANTS}

_last = [0.0]


def generate(**kwargs):
    """모델 호출 (무료 한도: 분당 15번 → 호출 사이를 4.2초 이상 띄움)"""
    wait = 4.2 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()
    return client.models.generate_content(model=MODEL, **kwargs)


class Week:
    """이번 주 점심 장부. guest_day에는 손님과 둘이 먹어서 2인분을 내요"""

    def __init__(self, budget=35000, guest_day=None):
        self.budget, self.guest_day = budget, guest_day
        self.visited = []  # [(요일, 식당)]

    def cost(self, day, name):
        return PRICE.get(name, 0) * (2 if day == self.guest_day else 1)

    @property
    def spent(self):
        return sum(self.cost(d, n) for d, n in self.visited)

    def pay(self, day, name):
        self.visited.append((day, name))

    def report(self):
        names = [n for _, n in self.visited]
        unknown = [n for n in names if n not in PRICE]
        over = self.spent > self.budget
        dup = len(names) != len(set(names))
        return {"visited": self.visited, "spent": self.spent, "over_budget": over, "duplicate": dup, "unknown": unknown,
                "rating": round(sum(RATING.get(n, 0) for n in names) / max(1, len(names)), 2),
                "ok": not over and not dup and not unknown and len(names) == 5}

    def rules(self):
        guest = f" {self.guest_day}요일에는 손님과 둘이 먹어서 그날은 2인분 값을 내." if self.guest_day else ""
        return f"월~금 5일 점심 합계 {self.budget}원 이하, 같은 식당은 한 주에 한 번만.{guest} 이왕이면 평점 높은 곳."


def list_restaurants() -> list[dict]:
    """회사 근처 식당 이름, 1인분 가격(원), 평점(5점 만점) 목록을 돌려준다."""
    return RESTAURANTS
