from groq import Groq
import os

def Grok_req(prompt: str, api_key) -> str:
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        
        result = ""
        for chunk in completion:
            result += chunk.choices[0].delta.content or ""
        return result
    except Exception as e:
        return f"오류 발생: {e}"


# 사용 예시
if __name__ == "__main__":
    # 예시: 환경 변수에서 API 키 불러오기
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise ValueError("LLM_API_KEY 환경 변수가 설정되지 않았습니다.")
    output = Grok_req("hello", api_key)
    print("Generated Response:", output)
