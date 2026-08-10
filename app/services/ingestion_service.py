from sqlalchemy.orm import Session

from app.services.parser_service import ParserService
from app.services.chunk_service import ChunkService
from app.services.vector_service import VectorService
from app.services.document_summary_service import DocumentSummaryService
from app.services.document_service import DocumentService

class IngestionService:

    def __init__(self):
        self.parser_service = ParserService()
        self.chunk_service = ChunkService()
        self.vector_service = VectorService()
        self.summary_service = DocumentSummaryService()
        self.document_service = DocumentService()

    def ingest(
        self,
        db,
        file_path,
        file_name,
        document_id
    ):

        # Step 1 - Parse OpenAPI
        parsed_data = self.parser_service.parse(file_path)

        # Step 2 - Create semantic chunks
        chunks = self.chunk_service.create_chunks(parsed_data)

        summary, embedding = self.summary_service.build_summary(
            file_name=file_name,
            chunks=chunks
        )

        document = self.document_service.get_document(
            db,
            document_id
        )

        document.summary = summary
        document.embedding = embedding

        db.commit()
        
        # Step 3 - Store in Vector DB
        self.vector_service.store_chunks(
            db=db,
            document_id=document_id,
            source_file=file_name,
            chunks=chunks
        )

        return {
            "file_name": file_name,
            "chunks_created": len(chunks),
            "message": "Document ingested successfully."
        }