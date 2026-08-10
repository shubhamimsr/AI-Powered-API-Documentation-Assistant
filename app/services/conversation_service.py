from sqlalchemy.orm import Session

from app.database.models import Conversation
from app.database.models import Message


class ConversationService:

    def create_conversation(
        self,
        db: Session,
        title: str = "New Chat"
    ):

        conversation = Conversation(title=title)

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    def get_conversation(
        self,
        db: Session,
        conversation_id: int
    ):

        return db.get(
            Conversation,
            conversation_id
        )

    def add_message(
        self,
        db: Session,
        conversation_id: int,
        role: str,
        content: str
    ):

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )

        db.add(message)
        db.commit()

    def history(
        self,
        db: Session,
        conversation_id: int
    ):

        conversation = self.get_conversation(
            db,
            conversation_id
        )

        if conversation is None:
            return []

        return conversation.messages[-10:]