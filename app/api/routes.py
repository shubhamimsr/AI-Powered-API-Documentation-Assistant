from pathlib import Path
import shutil

from fastapi import APIRouter, UploadFile, File, Depends
from app.services.embedding_service import EmbeddingService
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.ingestion_service import IngestionService
from pydantic import BaseModel, Field

from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.services.chat_service import ChatService
from app.services.hash_service import HashService
from app.services.document_service import DocumentService
from fastapi.responses import StreamingResponse
from io import BytesIO
from fastapi import HTTPException
document_service = DocumentService()

router = APIRouter()
embedding_service = EmbeddingService()


router = APIRouter()

UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(exist_ok=True)

ingestion_service = IngestionService()
hash_service = HashService()
document_service = DocumentService()

@router.get(
        "/",
        summary="Check the health of the system",
        description="Checks whether the system is online or not?"
    )
def health():
    return {
        "status": "running",
        "application": "APIMind AI"
    }

@router.get("/embedding-test")
def embedding_test():

    text = "Create a new user"

    embedding = embedding_service.get_embedding(text)

    return {
        "text": text,
        "dimension": len(embedding)
    }

@router.post(
        "/ingest",
        summary="Ingest or Upload the API documentation file",
        description="Upload the API documentation file.\nSupported type:- yaml, markdown, pdf"
    )
def ingest_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Read uploaded file once
    file_bytes = file.file.read()

    # Calculate SHA-256 hash
    file_hash = hash_service.calculate(file_bytes)

    # Check if already uploaded
    existing = document_service.exists(db, file_hash)

    if existing:
        return {
            "message": "Document already uploaded."
        }

    # Save document metadata
    document = document_service.save(
        db=db,
        filename=file.filename,
        file_hash=file_hash
    )

    # Save file to uploads directory
    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(file_bytes)

    # Continue normal ingestion
    return ingestion_service.ingest(
        db=db,
        file_path=file_path,
        file_name=file.filename,
        document_id=document.id
    )

retrieval_service = RetrievalService()
llm_service = LLMService()
chat_service = ChatService()

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        description="User question related to uploaded API documentation",
        examples=["Which endpoint lists models?"]
    )

    conversation_id: int | None = Field(
        default=None,
        description="Existing conversation id. Leave empty to create a new conversation."
    )

    source_file: str | None = Field(
        default=None,
        description="Optional filename to restrict search to one uploaded document.",
        examples=["openai.yaml"]
    )

@router.post(
        "/chat",
        summary="Ask questions about API documentation",
        description="""
            Uses RAG pipeline:\n
            --> |Creates query embedding            |
            --> |Performs vector similarity search  |
            --> |Retrieves relevant API chunks      |
            --> |Generates answer using LLM         |
        """
    )
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
   
    return chat_service.ask(
        db=db,
        question=request.question,
        conversation_id=request.conversation_id,
        source_file=request.source_file
    )

@router.post(
    "/chat/stream",
    summary="Stream AI response",
    description="""
                Streams the AI response token-by-token using Server Sent Events (SSE).
                Ideal for chat applications.
                """
)
def stream_chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    generator = chat_service.stream(
        db=db,
        question=request.question,
        conversation_id=request.conversation_id,
        source_file=request.source_file
    )

    return StreamingResponse(
        generator,
        media_type="text/plain"
    )

@router.get(
        "/documents",
        summary="List all the uploaded documents",
        description="Fetch all uploaded documents stored in the system."
)
def list_documents(
    db: Session = Depends(get_db)
):

    documents = document_service.list_documents(db)

    result = []

    for doc in documents:

        result.append({
            "id": doc.id,
            "file_name": doc.file_name,
            "uploaded_at": doc.uploaded_at,
            "chunks": document_service.chunk_count(
                db,
                doc.id
            )
        })

    return result

@router.get(
        "/documents/{document_id}",
        summary="Retrives a single document",
        description="Retrives metadata of a single document based on the Document-ID."
    )
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = document_service.get_document(
        db,
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "id": document.id,
        "file_name": document.file_name,
        "uploaded_at": document.uploaded_at,
        "chunks": document_service.chunk_count(
            db,
            document.id
        )
    }

@router.delete(
        "/documents/{document_id}",
        summary="Delete uploaded document",
        description="Delete/remove a particular document, based on the Document-ID."
    )
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    deleted = document_service.delete_document(
        db,
        document_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "message": "Document deleted successfully."
    }