from openai import OpenAI

from app.config import (
    BASE_URL,
    MODEL_NAME,
    OPENAI_API_KEY
)

from app.prompts import SYSTEM_PROMPT
from app.services.prompt_service import PromptService


class LLMService:

    def __init__(self):

        self.client = OpenAI(
            base_url=BASE_URL,
            api_key=OPENAI_API_KEY
        )

        # Store the model name once and reuse it everywhere
        self.model = MODEL_NAME

        self.prompt = PromptService()

    def ask(
        self,
        question: str,
        contexts,
        history
    ):

        user_prompt = self.prompt.build(
            question=question,
            chunks=contexts,
            history=history
        )

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        return response.choices[0].message.content.strip()

    def stream_answer(
        self,
        question: str,
        contexts,
        history
    ):

        user_prompt = self.prompt.build(
            question=question,
            chunks=contexts,
            history=history
        )

        stream = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            stream=True,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        for chunk in stream:

            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta.content

            if delta:
                yield delta

    def verify_grounding(
        self,
        question: str,
        answer: str,
        contexts
    ) -> bool:

        context = "\n\n".join(
            chunk["chunk_text"]
            for chunk in contexts
        )

        prompt = f"""
You are a strict evaluator.

Determine whether the ANSWER is fully supported by the DOCUMENTATION.

Rules:

- Use ONLY the documentation.
- Ignore outside knowledge.
- If any important statement in the answer is unsupported, reply NO.
- Reply ONLY with YES or NO.

DOCUMENTATION

{context}

QUESTION

{question}

ANSWER

{answer}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You verify whether answers are grounded in documentation."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result = response.choices[0].message.content.strip().upper()

        print(f"\nGrounding Check: {result}")

        return result.startswith("YES")