import httpx


class RAGClient:

    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"

    def ask(
        self,
        question: str,
        conversation_id: int = 0,
        source_file: str | None = None
    ):

        payload = {
            "question": question,
            "conversation_id": conversation_id,
            "source_file": source_file
        }

        response = httpx.post(
            f"{self.base_url}/chat",
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        return response.json()