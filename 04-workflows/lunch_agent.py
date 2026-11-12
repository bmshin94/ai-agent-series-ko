# 4편: 에이전트 방식 — 다음에 무엇을 할지 '모델'이 정해요 (1~3편 루프와 같음, 모델 호출 수·토큰을 세도록만 바꿈)
# 준비: pip install google-genai / 환경변수 GOOGLE_API_KEY
# 실행: python lunch_agent.py
from google.genai import types

from lunch_tools import MODEL, TOOLS, client

MAX_STEPS = 6
GOAL = ("지갑에 있는 돈으로 둘이 같이 먹을 수 있고, 회사에서 걸어서 10분 안에 갈 수 있는 점심 메뉴 골라줘. "
        "마지막 줄은 '최종 선택: 식당이름'으로 끝내 줘.")


def run_agent(goal: str, tool_list: list = TOOLS, verbose: bool = True) -> dict:
    tools = {f.__name__: f for f in tool_list}
    history = [types.Content(role="user", parts=[types.Part(text=goal)])]
    config = types.GenerateContentConfig(
        tools=tool_list,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    calls, tokens = 0, 0
    for step in range(1, MAX_STEPS + 1):
        response = client.models.generate_content(model=MODEL, contents=history, config=config)
        calls += 1
        tokens += response.usage_metadata.total_token_count or 0
        history.append(response.candidates[0].content)

        if not response.function_calls:
            return {"answer": response.text, "model_calls": calls, "tokens": tokens}

        for call in response.function_calls:
            result = tools[call.name](**call.args)
            if verbose:
                print(f"[{step}단계] 모델이 고름: {call.name}({dict(call.args)}) → {result}")
            history.append(types.Content(role="user", parts=[
                types.Part.from_function_response(name=call.name, response={"result": result})
            ]))

    return {"answer": f"{MAX_STEPS}단계 안에 끝내지 못해서 멈췄어요.", "model_calls": calls, "tokens": tokens}


if __name__ == "__main__":
    r = run_agent(GOAL)
    print(r["answer"])
    print(f"(모델 호출 {r['model_calls']}번, 토큰 {r['tokens']}개)")
