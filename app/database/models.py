from sqlalchemy import Column, Integer, Text, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from pgvector.sqlalchemy import Vector
from app.database.db import Base
from sqlalchemy import LargeBinary

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True)

    document_id = Column(
        Integer,
        ForeignKey("uploaded_documents.id"),
        nullable=False
    )

    source_file = Column(String, nullable=False)

    chunk_type = Column(String, nullable=False)

    endpoint = Column(String)

    method = Column(String)

    chunk_text = Column(Text, nullable=False)

    embedding = Column(Vector(1024), nullable=False)

    document = relationship(
        "UploadedDocument",
        back_populates="chunks"
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)

    title = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id")
    )

    role = Column(String)

    content = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )

class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(Integer, primary_key=True)

    file_name = Column(String, nullable=False)

    file_hash = Column(String(64), unique=True, nullable=False)

    summary = Column(Text)

    embedding = Column(Vector(1024))

    uploaded_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan"
    )