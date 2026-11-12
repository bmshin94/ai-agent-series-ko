# 4편: 요청 모양이 바뀌면? — 정해진 길만 가는 워크플로 vs 길을 그때그때 정하는 에이전트
# 실행: python open_request.py
import time

from lunch_agent import run_agent
from lunch_tools import TOOLS, get_menu_tags
from lunch_workflow import run_workflow

REQUEST = ("오늘은 혼자 먹을 거야. 비가 와서 걸어서 8분 안이면 좋겠고, 따뜻한 국물에 밥이 있는 곳으로. "
           "지갑에 있는 돈으로 낼 수 있어야 해. 마지막 줄은 '최종 선택: 식당이름'으로 끝내 줘.")

print(f"요청: {REQUEST}\n")
print("=== 워크플로 (둘이·10분 기준으로 짜 둔 길) ===")
print(run_workflow()["answer"])
time.sleep(20)
print("\n=== 에이전트 (메뉴 종류 도구 하나 추가) ===")
r = run_agent(REQUEST, TOOLS + [get_menu_tags])
print(r["answer"])
print(f"(모델 호출 {r['model_calls']}번, 토큰 {r['tokens']}개)")
