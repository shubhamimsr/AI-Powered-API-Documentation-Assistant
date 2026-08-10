from sqlalchemy.orm import Session

from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from app.services.conversation_service import ConversationService
from app.services.document_resolver import DocumentResolver
from app.services.confidence_service import ConfidenceService
from app.services.context_compression_service import ContextCompressionService
from app.config import MIN_CONFIDENCE


class ChatService:

    def __init__(self):

        self.retrieval = RetrievalService()
        self.llm = LLMService()
        self.conversation = ConversationService()
        self.document_resolver = DocumentResolver()
        self.confidence = ConfidenceService()
        self.context_compression = ContextCompressionService()

    # ===========================================================
    # NORMAL CHAT
    # ===========================================================

    def ask(
        self,
        db: Session,
        question: str,
        conversation_id: int | None,
        source_file: str | None = None
    ):

        # -----------------------------
        # Conversation
        # -----------------------------

        if conversation_id is None or conversation_id <= 0:

            conversation = self.conversation.create_conversation(db)
            conversation_id = conversation.id

        history = self.conversation.history(
            db,
            conversation_id
        )

        # -----------------------------
        # Document Resolver
        # -----------------------------

        if not source_file:

            source_file = self.document_resolver.resolve(
                db=db,
                question=question
            )

            if source_file:
                print(f"Resolved document: {source_file}")
            else:
                print("Searching across all uploaded documents.")

        # -----------------------------
        # Retrieval
        # -----------------------------

        chunks = self.retrieval.retrieve(
            db=db,
            query=question,
            source_file=source_file
        )
        compressed_chunks = self.context_compression.compress(
            question=question,
            chunks=chunks
        )

        # -----------------------------
        # Confidence
        # -----------------------------

        confidence = self.confidence.calculate(chunks)

        print(f"\nConfidence Score : {confidence:.4f}")

        # -----------------------------
        # Low Confidence
        # -----------------------------

        if confidence < MIN_CONFIDENCE:

            answer = (
                "I couldn't find enough evidence in the uploaded "
                "documentation to answer this question."
            )

        else:

            # -----------------------------
            # Generate Answer
            # -----------------------------

            answer = self.llm.ask(
                question,
                compressed_chunks,
                history
            )

            # -----------------------------
            # Grounding Verification
            # -----------------------------

            grounded = self.llm.verify_grounding(
                question=question,
                answer=answer,
                contexts=chunks
            )

            print("Grounded :", grounded)

            if not grounded:

                answer = (
                    "The generated answer could not be verified "
                    "against the uploaded documentation."
                )

        # -----------------------------
        # Save Conversation
        # -----------------------------

        self.conversation.add_message(
            db,
            conversation_id,
            "user",
            question
        )

        self.conversation.add_message(
            db,
            conversation_id,
            "assistant",
            answer
        )

        # -----------------------------
        # Response
        # -----------------------------

        return {
            "conversation_id": conversation_id,
            "confidence": round(confidence, 3),
            "answer": answer,
            "sources": [
                {
                    "endpoint": chunk["endpoint"],
                    "method": chunk["method"],
                    "source_file": chunk["source_file"]
                }
                for chunk in chunks
            ]
        }

    # ===========================================================
    # STREAMING
    # ===========================================================

    def stream(
        self,
        db: Session,
        question: str,
        conversation_id: int | None,
        source_file: str | None = None
    ):

        # -----------------------------
        # Conversation
        # -----------------------------

        if conversation_id is None or conversation_id <= 0:

            conversation = self.conversation.create_conversation(db)
            conversation_id = conversation.id

        history = self.conversation.history(
            db,
            conversation_id
        )

        # -----------------------------
        # Document Resolver
        # -----------------------------

        if not source_file:

            source_file = self.document_resolver.resolve(
                db=db,
                question=question
            )

            if source_file:
                print(f"Resolved document: {source_file}")
            else:
                print("Searching across all uploaded documents.")

        # -----------------------------
        # Retrieval
        # -----------------------------

        chunks = self.retrieval.retrieve(
            db=db,
            query=question,
            source_file=source_file
        )

        compressed_chunks = self.context_compression.compress(
            question=question,
            chunks=chunks
        )

        # -----------------------------
        # Confidence
        # -----------------------------

        confidence = self.confidence.calculate(chunks)

        print(f"\nConfidence Score : {confidence:.4f}")

        # -----------------------------
        # Low Confidence
        # -----------------------------

        if confidence < MIN_CONFIDENCE:

            message = (
                "I couldn't find enough evidence in the uploaded "
                "documentation to answer this question."
            )

            yield message

            self.conversation.add_message(
                db,
                conversation_id,
                "user",
                question
            )

            self.conversation.add_message(
                db,
                conversation_id,
                "assistant",
                message
            )

            return

        # -----------------------------
        # Stream Response
        # -----------------------------

        stream = self.llm.stream_answer(
            question,
            compressed_chunks,
            history
        )

        complete_answer = ""

        for token in stream:

            complete_answer += token

            yield token

        # -----------------------------
        # Grounding Verification
        # -----------------------------

        grounded = self.llm.verify_grounding(
            question=question,
            answer=complete_answer,
            contexts=chunks
        )

        print("Grounded :", grounded)

        if not grounded:

            complete_answer = (
                "The generated answer could not be verified "
                "against the uploaded documentation."
            )

        # -----------------------------
        # Save Conversation
        # -----------------------------

        self.conversation.add_message(
            db,
            conversation_id,
            "user",
            question
        )

        self.conversation.add_message(
            db,
            conversation_id,
            "assistant",
            complete_answer
        )