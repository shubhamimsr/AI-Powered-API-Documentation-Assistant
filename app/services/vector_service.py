from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.models import DocumentChunk
from app.services.embedding_service import EmbeddingService


class VectorService:

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def store_chunks(
        self,
        db: Session,
        document_id: int,
        source_file: str,
        chunks
    ):

        texts = [chunk["text"] for chunk in chunks]

        embeddings = self.embedding_service.get_embeddings(texts)

        for chunk, embedding in zip(chunks, embeddings):

            document_chunk = DocumentChunk(
                document_id=document_id,
                source_file=source_file,
                chunk_type=chunk["chunk_type"],
                endpoint=chunk["endpoint"],
                method=chunk["method"],
                chunk_text=chunk["text"],
                embedding=embedding
            )
            db.add(document_chunk)
        db.commit()

   

    def search(
        self,
        db: Session,
        query: str,
        source_files: list[str] | None = None,
        limit: int = 5
    ):

        query_embedding = self.embedding_service.get_embedding(query)

        if source_files:
            sql = text("""
                SELECT *
                FROM document_chunks
                WHERE source_file = ANY(:source_files)
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :limit
            """)

            params = {
                "embedding": str(query_embedding),
                "source_files": source_files,
                "limit": limit
            }

        else:
            sql = text("""
                SELECT *
                FROM document_chunks
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :limit
            """)

            params = {
                "embedding": str(query_embedding),
                "limit": limit
            }

        result = db.execute(sql, params).mappings().all()
        return result

        # return result.mappings().all()

    
    def keyword_search(
        self,
        db: Session,
        query: str,
        source_files: list[str] | None = None,
        limit: int = 5
    ):


        if source_files:

            sql = text("""
                    SELECT *,
                        ts_rank(
                            to_tsvector('english', chunk_text),
                            plainto_tsquery('english', :query)
                        ) AS rank
                    FROM document_chunks
                    WHERE source_file = ANY(:source_files)
                    AND to_tsvector('english', chunk_text)
                        @@ plainto_tsquery('english', :query)
                    ORDER BY rank DESC
                    LIMIT :limit
                """)

            params = {
                "query": query,
                "source_files": source_files,
                "limit": limit
            }

        else:

            sql = text("""
                    SELECT *,
                        ts_rank(
                            to_tsvector('english', chunk_text),
                            plainto_tsquery('english', :query)
                        ) AS rank
                    FROM document_chunks
                    WHERE to_tsvector('english', chunk_text)
                        @@ plainto_tsquery('english', :query)
                    ORDER BY rank DESC
                    LIMIT :limit
                """)

            params = {
                "query": query,
                "limit": limit
            }

        result = db.execute(sql, params).mappings().all()
        return result