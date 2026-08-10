from sentence_transformers import SentenceTransformer


class EmbeddingService:
    _model = None

    def __init__(self):
        if EmbeddingService._model is None:
            EmbeddingService._model = SentenceTransformer("BAAI/bge-m3")

    def get_embedding(self, text: str) -> list[float]:
        embedding = EmbeddingService._model.encode(text)
        return embedding.tolist()

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        embeddings = EmbeddingService._model.encode(texts)
        return embeddings.tolist()