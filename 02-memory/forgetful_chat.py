# 실험: 모델은 지난 대화를 기억할까? — 같은 질문을 '기록 없이' 한 번, '기록과 함께' 한 번
from google import genai
from google.genai import types

client = genai.Client()
MODEL = "gemini-flash-lite-latest"


def ask(contents):
    return client.models.generate_content(model=MODEL, contents=contents).text


# 1) 첫 번째 요청: 어제 점심 이야기를 들려준다
first = "어제 점심은 김밥천국에서 먹었어. 한 줄로만 대답해 줘."
first_answer = ask(first)
print("나:", first)
print("AI:", first_answer)

# 2) 두 번째 요청: 방금 한 말을 물어본다 (기록 없이 질문만 보냄)
question = "내가 어제 점심 어디서 먹었다고 했지? 한 줄로만 대답해 줘."
print("\n[기록 없이] 나:", question)
print("AI:", ask(question))

# 3) 같은 질문을, 지금까지의 대화 기록과 함께 보냄 = 단기 기억
history = [
    types.Content(role="user", parts=[types.Part(text=first)]),
    types.Content(role="model", parts=[types.Part(text=first_answer)]),
    types.Content(role="user", parts=[types.Part(text=question)]),
]
print("\n[기록과 함께] 나:", question)
print("AI:", ask(history))
