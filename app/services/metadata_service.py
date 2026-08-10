import re


class MetadataService:

    METHODS = [
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]

    def extract(
        self,
        question: str
    ):

        metadata = {}

        upper = question.upper()

        # ------------------------
        # HTTP Method
        # ------------------------

        for method in self.METHODS:

            if method in upper:
                metadata["method"] = method
                break

        # ------------------------
        # Endpoint
        # ------------------------

        endpoint = re.search(
            r"/[A-Za-z0-9_/\-]+",
            question
        )

        if endpoint:

            metadata["endpoint"] = endpoint.group()

        return metadata