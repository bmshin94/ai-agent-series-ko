# 비교용: 도구도 반복문도 없는 '그냥 챗봇' — 모델을 딱 한 번 부르고 끝
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-flash-lite-latest",
    contents="지갑에 있는 돈으로 둘이 같이 먹을 점심 메뉴 골라줘. 이유도 알려줘.",
)
print(response.text)
