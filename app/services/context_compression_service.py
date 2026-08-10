import re

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


class ContextCompressionService:

    _model = None

    def __init__(self):

        if ContextCompressionService._model is None:

            print("Loading Context Compression model...")

            ContextCompressionService._model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )

    def compress(
        self,
        question: str,
        chunks: list,
        top_sentences: int = 3
    ):

        if not chunks:
            return []

        question_embedding = (
            ContextCompressionService._model.encode(
                question,
                convert_to_tensor=True
            )
        )

        compressed_chunks = []

        for chunk in chunks:

            text = chunk["chunk_text"]

            sentences = [
                sentence.strip()
                for sentence in re.split(
                    r'(?<=[.!?])\s+',
                    text
                )
                if sentence.strip()
            ]

            if len(sentences) <= top_sentences:
                compressed_chunks.append(chunk)
                continue

            sentence_embeddings = (
                ContextCompressionService._model.encode(
                    sentences,
                    convert_to_tensor=True
                )
            )

            similarities = cos_sim(
                question_embedding,
                sentence_embeddings
            )[0]

            ranked = sorted(
                zip(sentences, similarities),
                key=lambda x: float(x[1]),
                reverse=True
            )

            best_sentences = [
                sentence
                for sentence, score in ranked[:top_sentences]
            ]

            compressed = dict(chunk)

            compressed["chunk_text"] = "\n".join(best_sentences)

            compressed_chunks.append(compressed)

        print("\n========== CONTEXT COMPRESSION ==========\n")

        for chunk in compressed_chunks:

            print(chunk["endpoint"])
            print(chunk["chunk_text"])
            print("--------------------------------------")

        return compressed_chunks