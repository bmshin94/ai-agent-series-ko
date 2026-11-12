# 4편: 워크플로 방식 — 같은 점심 문제를, 순서를 '코드'가 정하게 다시 짰어요
# 1~3단계는 그냥 파이썬이고, 모델은 마지막에 추천 문구를 쓸 때 한 번만 불러요
# 실행: python lunch_workflow.py
from lunch_tools import MODEL, WALK_MINUTES, check_wallet, client, list_restaurants

PEOPLE = 2
MAX_MINUTES = 10


def run_workflow(verbose: bool = True) -> dict:
    # 1단계: 필요한 정보를 코드가 직접 가져와요 (모델에게 물어볼 필요 없음)
    restaurants = list_restaurants()
    budget = check_wallet()

    # 2단계: 조건 검사도 코드가 해요 — 둘이 먹을 수 있나? 걸어서 10분 안인가?
    candidates = [r for r in restaurants
                  if r["price"] * PEOPLE <= budget and WALK_MINUTES[r["name"]] <= MAX_MINUTES]
    if verbose:
        print(f"[1단계] 식당 {len(restaurants)}곳, 지갑 {budget}원")
        print(f"[2단계] 조건 통과: {[r['name'] for r in candidates]}")
    if not candidates:
        return {"answer": "조건에 맞는 식당이 없어요.", "model_calls": 0, "tokens": 0}
    pick = min(candidates, key=lambda r: r["price"])

    # 3단계: 사람에게 보여줄 추천 문구만 모델이 써요 — 여기서 딱 한 번
    prompt = (f"점심 추천 문구를 두 문장으로 써 줘. 식당: {pick['name']}, 둘이 {pick['price'] * PEOPLE}원, "
              f"걸어서 {WALK_MINUTES[pick['name']]}분. 마지막 줄은 '최종 선택: {pick['name']}'으로 끝내 줘.")
    response = client.models.generate_content(model=MODEL, contents=prompt)
    if verbose:
        print("[3단계] 모델에게 추천 문구 요청 (모델 호출 1번)")
    return {"answer": response.text, "model_calls": 1, "tokens": response.usage_metadata.total_token_count or 0}


if __name__ == "__main__":
    r = run_workflow()
    print(r["answer"])
    print(f"(모델 호출 {r['model_calls']}번, 토큰 {r['tokens']}개)")
