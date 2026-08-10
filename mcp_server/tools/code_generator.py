from services.rag_client import RAGClient

client = RAGClient()


def generate_api_code(
    question: str,
    language: str,
    source_file: str = ""
):

    result = client.ask(
        question=question,
        conversation_id=0,
        source_file=source_file if source_file else None
    )

    return {
        "language": language,
        "answer": result["answer"],
        "sources": result["sources"]
    }