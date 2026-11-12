# 3편: 되돌릴 수 없는 도구는 사람 확인 — 예약 도구는 실행 전에 꼭 물어봐요
# 실행: python confirm_agent.py
from walk_agent import BASE, get_walking_minutes_v3, run_agent


def reserve_table(restaurant_name: str, people: int) -> str:
    """식당에 자리를 예약한다. 되돌릴 수 없으니 사용자가 고른 식당이 확실할 때만 부른다.
    restaurant_name은 list_restaurants의 name 그대로, people은 인원 수."""
    answer = input(f"\n⚠️  {restaurant_name}에 {people}명 예약할까요? (y/n) ").strip().lower()
    if answer != "y":
        return "사용자가 예약을 거절했어요. 예약하지 말고 다른 방법을 물어보세요."
    return f"{restaurant_name} {people}명 예약 완료"


if __name__ == "__main__":
    goal = ("지갑에 있는 돈으로 둘이 같이 먹을 수 있고, 회사에서 걸어서 10분 안에 갈 수 있는 곳을 골라서 "
            "2명 자리 예약까지 해 줘.")
    print(run_agent(goal, BASE + [get_walking_minutes_v3, reserve_table]))
