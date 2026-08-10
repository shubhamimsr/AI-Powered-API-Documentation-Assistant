class PromptService:

    def build(
        self,
        question: str,
        chunks,
        history
    ):

        # ----------------------------
        # Conversation History
        # ----------------------------

        conversation = "\n".join(
            f"{message.role}: {message.content}"
            for message in history
        )

        # ----------------------------
        # Retrieved Context
        # ----------------------------

        context_blocks = []

        for i, chunk in enumerate(chunks, start=1):

            context_blocks.append(
                f"""
                    Document [{i}]

                    Source File:
                    {chunk["source_file"]}

                    Endpoint:
                    {chunk["method"]} {chunk["endpoint"]}

                    Content:
                    {chunk["chunk_text"]}
            """
            )

        context = "\n\n".join(context_blocks)

        prompt = f"""
                Conversation History
                --------------------
                {conversation}

                Retrieved Documentation
                -----------------------
                {context}

                User Question
                -------------
                {question}

                Instructions

                1. Answer ONLY from the retrieved documentation.
                2. Never invent information.
                3. If the answer is unavailable, reply:
                "I don't know based on the uploaded documentation."
                4. Mention the HTTP method whenever applicable.
                5. Mention the endpoint whenever applicable.
                6. Every factual statement must be supported by the retrieved documentation.
                7. Whenever information comes from one of the retrieved documents,
                append a citation such as:

                [1]
                [2]

                8. At the end include a "References" section.

                For each reference, use ONLY the retrieved documents and follow this format:

                [n] <source_file> — <HTTP_METHOD> <endpoint>

                Example format only:

                [1] filename.yaml — GET /resource
                [2] another-file.yaml — POST /resource/{id}

                9. Never invent endpoints, filenames, methods, or references.

                10. Every reference MUST correspond to one of the retrieved documentation blocks above.
                """

        return prompt