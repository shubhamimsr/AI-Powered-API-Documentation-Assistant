from openai import OpenAI

from app.config import (
    BASE_URL,
    OPENAI_API_KEY,
    MODEL_NAME
)


class QueryRewriter:

    def __init__(self):

        self.client = OpenAI(
            base_url=BASE_URL,
            api_key=OPENAI_API_KEY
        )

    def rewrite(
        self,
        question: str
    ) -> str:

        messages = [
            {
                "role": "system",
                "content": """
You are an expert search query optimizer.

Your job is to rewrite a user's question into a short search query
for retrieving API documentation.

Rules:

- Keep important nouns.
- Preserve endpoint names if present.
- Preserve HTTP methods if present.
- Remove unnecessary words.
- Never answer the question.
- Return ONLY the rewritten query.
"""
            },
            {
                "role": "user",
                "content": question
            }
        ]

        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0,
            messages=messages
        )

        return response.choices[0].message.content.strip()