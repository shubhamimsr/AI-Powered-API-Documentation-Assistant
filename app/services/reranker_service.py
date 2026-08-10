from sentence_transformers import CrossEncoder


class RerankerService:

    _model = None

    def __init__(self):

        if RerankerService._model is None:

            print("Loading CrossEncoder...")

            RerankerService._model = CrossEncoder(
                "cross-encoder/ms-marco-MiniLM-L-6-v2"
            )

    def rerank(
        self,
        question: str,
        chunks: list,
        top_k: int = 3
    ):

        if not chunks:
            return []

        pairs = [
            (
                question,
                chunk["chunk_text"]
            )
            for chunk in chunks
        ]

        scores = RerankerService._model.predict(pairs)

        ranked = sorted(
            zip(chunks, scores),
            key=lambda x: x[1],
            reverse=True
        )

        print("\n========== RERANKING ==========\n")

        results = []

        for chunk, score in ranked:

            print(
                f"{score:.4f}",
                chunk["endpoint"],
                chunk["method"]
            )

            # Copy the chunk so we don't mutate the original object
            item = dict(chunk)

            # Store reranker score
            item["rerank_score"] = float(score)

            results.append(item)

        return results[:top_k]