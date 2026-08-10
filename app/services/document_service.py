from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import UploadedDocument
from app.database.models import DocumentChunk
from sqlalchemy import text
from app.services.embedding_service import EmbeddingService

class DocumentService:

    def __init__(self):
        self.embedding = EmbeddingService()

    def exists(
        self,
        db: Session,
        file_hash: str
    ):
        return (
            db.query(UploadedDocument)
            .filter(UploadedDocument.file_hash == file_hash)
            .first()
        )

    def save(
        self,
        db: Session,
        filename: str,
        file_hash: str,
        summary: str | None = None,
        embedding: list[float] | None = None
    ):
        document = UploadedDocument(
            file_name=filename,
            file_hash=file_hash,
            summary=summary,
            embedding=embedding
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    def list_documents(
        self,
        db: Session
    ):
        return db.query(UploadedDocument).all()

    def get_document(
        self,
        db: Session,
        document_id: int
    ):
        return db.get(
            UploadedDocument,
            document_id
        )

    def chunk_count(
        self,
        db: Session,
        document_id: int
    ):
        return (
            db.query(func.count(DocumentChunk.id))
            .filter(DocumentChunk.document_id == document_id)
            .scalar()
        )

    def delete_document(
        self,
        db: Session,
        document_id: int
    ):
        document = self.get_document(
            db,
            document_id
        )

        if document is None:
            return False

        db.delete(document)
        db.commit()

        return True

    def find_relevant_documents(
        self,
        db: Session,
        question: str,
        limit: int = 2
    ):

        query_embedding = self.embedding.get_embedding(question)

        sql = text("""
                SELECT
                    id,
                    file_name
                FROM uploaded_documents
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :limit
            """)

        rows = db.execute(
            sql,
            {
                "embedding": str(query_embedding),
                "limit": limit
            }
        ).mappings().all()

        return rows