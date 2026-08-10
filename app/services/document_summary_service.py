from app.services.embedding_service import EmbeddingService


class DocumentSummaryService:

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def build_summary(
        self,
        file_name: str,
        chunks
    ):

        endpoints = []
        methods = set()

        for chunk in chunks:

            endpoint = chunk.get("endpoint")
            method = chunk.get("method")

            if endpoint:
                endpoints.append(endpoint)

            if method:
                methods.add(method)

        endpoints = endpoints[:10]

        summary = f"""
                    File: {file_name}

                    Endpoints:
                    {", ".join(endpoints)}

                    HTTP Methods:
                    {", ".join(sorted(methods))}
                """

        embedding = self.embedding_service.get_embedding(summary)

        return summary, embedding