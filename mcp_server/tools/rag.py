from services.rag_client import RAGClient

client = RAGClient()


def search_api_documentation(
    question: str,
    source_file: str = ""
):

    if source_file.strip() == "":
        source_file = None

    result = client.ask(
        question=question,
        conversation_id=0,
        source_file=source_file
    )

    return result