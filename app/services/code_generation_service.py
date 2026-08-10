from app.services.llm_service import LLMService


class CodeGenerationService:

    def __init__(self):
        self.llm = LLMService()

    def generate(
        self,
        language: str,
        question: str,
        chunks
    ):

        context = "\n\n".join(
            chunk["chunk_text"]
            for chunk in chunks
        )

        prompt = f"""
You are an API SDK generator.

Use ONLY the API documentation below.

Documentation:
{context}

Task:
Generate production-quality {language} code.

Requirements:
- Include imports
- Show authentication
- Show request body
- Show error handling
- Use best practices

Question:
{question}

Code:
"""

        response = self.llm.client.chat.completions.create(
            model=self.llm.client_model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "Generate accurate API code."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content