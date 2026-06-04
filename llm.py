from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL


client = Groq(api_key=GROQ_API_KEY)


def ask_llm(
    user_message,
    system_message="You are CollegeOS Agent, a helpful college assistant. Keep replies clear and practical.",
    temperature=0.3,
    max_tokens=500
):
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    answer = response.choices[0].message.content

    return answer