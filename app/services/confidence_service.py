class ConfidenceService:

    def calculate(self, chunks):

        if not chunks:
            return 0.0

        scores = []

        for chunk in chunks:

            score = chunk.get("rerank_score")

            if score is not None:
                scores.append(score)

        if not scores:
            return 0.50

        return max(scores)