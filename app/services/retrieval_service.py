from app.services.vector_service import VectorService
from app.services.reranker_service import RerankerService
from app.services.document_service import DocumentService
from app.config import VECTOR_TOP_K
from app.config import RERANK_TOP_K
from app.config import RRF_K
from app.config import USE_RERANKER
from app.services.query_rewriter import QueryRewriter
from app.config import USE_QUERY_REWRITER

class RetrievalService:

   

    def __init__(self):
        self.vector = VectorService()
        self.reranker = RerankerService()
        self.document = DocumentService()
        self.query_rewriter = QueryRewriter()

    def retrieve(
        self,
        db,
        query,
        source_file=None
    ):

        # ---------------------------------
        # Query Rewriting
        # ---------------------------------

        search_query = query

        if USE_QUERY_REWRITER:
            try:
                rewritten = self.query_rewriter.rewrite(query)
                if rewritten:
                    search_query = rewritten
            except Exception as ex:
                print("Query Rewriter Error:", ex)

        print("\nOriginal Query :", query)
        print("Search Query   :", search_query)

        # ---------------------------------
        # Automatic Document Selection
        # ---------------------------------

        selected_documents = None

        if source_file:
            selected_documents = [source_file]
        else:
            documents = self.document.find_relevant_documents(
                db=db,
                question=search_query,
                limit=2
            )
            selected_documents = [
                doc["file_name"]
                for doc in documents
            ]
        print("\nSelected Documents")
        for doc in selected_documents:
            print("-", doc)

        # -----------------------------
        # Semantic Search
        # -----------------------------

        vector_results = self.vector.search(
            db=db,
            query=search_query,
            source_files=selected_documents,
            limit=VECTOR_TOP_K
        )

        # -----------------------------
        # Keyword Search
        # -----------------------------

        keyword_results = self.vector.keyword_search(
            db=db,
            query=search_query,
            source_files=selected_documents,
            limit=VECTOR_TOP_K
        )

        # -----------------------------
        # Reciprocal Rank Fusion
        # -----------------------------

        fused = self.reciprocal_rank_fusion(
            vector_results,
            keyword_results
        )

        # -----------------------------
        # Cross Encoder Reranking
        # -----------------------------

        if USE_RERANKER:
            reranked = self.reranker.rerank(
                question=query,
                chunks=fused,
                top_k=RERANK_TOP_K
            )
        else:
            reranked = fused[:RERANK_TOP_K]

        print("\n========== FINAL CHUNKS ==========\n")

        if not reranked:
            print("NO CHUNKS FOUND")

        for chunk in reranked:

            print("Endpoint :", chunk["endpoint"])
            print("Method   :", chunk["method"])
            print("Source   :", chunk["source_file"])
            print(chunk["chunk_text"][:250])
            print("----------------------------------")

        return reranked

    def reciprocal_rank_fusion(
        self,
        vector_results,
        keyword_results
    ):

        scores = {}

        # Vector Search Score

        for rank, row in enumerate(vector_results, start=1):

            doc_id = row["id"]

            if doc_id not in scores:

                scores[doc_id] = {
                    "document": row,
                    "score": 0
                }

            scores[doc_id]["score"] += 1 / (RRF_K + rank)

        # Keyword Search Score

        for rank, row in enumerate(keyword_results, start=1):

            doc_id = row["id"]

            if doc_id not in scores:

                scores[doc_id] = {
                    "document": row,
                    "score": 0
                }

            scores[doc_id]["score"] += 1 / (RRF_K + rank)

        ranked = sorted(
            scores.values(),
            key=lambda x: x["score"],
            reverse=True
        )

        return [
            item["document"]
            for item in ranked
        ]