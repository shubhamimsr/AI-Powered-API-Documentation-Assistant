from openai import OpenAI

from app.config import (
    BASE_URL,
    OPENAI_API_KEY,
    MODEL_NAME
)


class MultiQueryService:

    def __init__(self):

        self.client = OpenAI(
            base_url=BASE_URL,
            api_key=OPENAI_API_KEY
        )

    def generate(
        self,
        question: str,
        max_queries: int = 4
    ) -> list[str]:

        messages = [
            {
                "role": "system",
                "content": f"""
                        You are an API documentation retrieval expert.

                        Generate {max_queries} different search queries that could retrieve
                        the correct API documentation.

                        Rules:

                        - Each query should express the same intent.
                        - Use different wording.
                        - Keep each query short.
                        - Preserve endpoint names if present.
                        - Preserve HTTP methods if present.
                        - Return ONLY one query per line.
                        - No numbering.
                        - No explanations.
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

        queries = []

        for line in response.choices[0].message.content.split("\n"):

            line = line.strip()

            if line:
                queries.append(line)

        if question not in queries:
            queries.insert(0, question)

        return queries