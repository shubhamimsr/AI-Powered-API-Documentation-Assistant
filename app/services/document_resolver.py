from sqlalchemy.orm import Session

from app.database.models import UploadedDocument


class DocumentResolver:

    def resolve(
        self,
        db: Session,
        question: str
    ):

        question = question.lower()

        documents = db.query(
            UploadedDocument
        ).all()

        for document in documents:

            filename = document.file_name.lower()

            name_without_extension = filename.split(".")[0]

            if filename in question:
                return document.file_name

            if name_without_extension in question:
                return document.file_name

        return None