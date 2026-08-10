import json


class ChunkService:

    def create_chunks(self, parsed_data: list[dict]) -> list[dict]:

        chunks = []

        for item in parsed_data:

            chunk_type = item["type"]

            if chunk_type == "endpoint":
                chunks.append({
                    "chunk_type": "endpoint",
                    "endpoint": item["endpoint"],
                    "method": item["method"],
                    "text": self._endpoint_chunk(item)
                })

            elif chunk_type == "security":
                chunks.append({
                    "chunk_type": "security",
                    "endpoint": None,
                    "method": None,
                    "text": self._security_chunk(item)
                })

            elif chunk_type == "schema":
                chunks.append({
                    "chunk_type": "schema",
                    "endpoint": None,
                    "method": None,
                    "text": self._schema_chunk(item)
                })

        return chunks

    def _endpoint_chunk(self, endpoint: dict) -> str:

        return f"""
        Endpoint: {endpoint['method']} {endpoint['endpoint']}

        Summary:
        {endpoint['summary']}

        Description:
        {endpoint['description']}

        Parameters:
        {json.dumps(endpoint['parameters'], indent=2)}

        Request Body:
        {json.dumps(endpoint['request_body'], indent=2)}

        Responses:
        {json.dumps(endpoint['responses'], indent=2)}

        Security:
        {json.dumps(endpoint['security'], indent=2)}
            """.strip()

    def _security_chunk(self, security: dict) -> str:

        return f"""
                Security Scheme: {security['name']}

                Details:
                {json.dumps(security['content'], indent=2)}
            """.strip()

    def _schema_chunk(self, schema: dict) -> str:
        return f"""
                Schema: {schema['name']}

                Definition:
                {json.dumps(schema['content'], indent=2)}
            """.strip()