import json
import yaml


class ParserService:

    def parse(self, file_path: str) -> list[dict]:

        if file_path.endswith(".yaml") or file_path.endswith(".yml"):
            with open(file_path, "r", encoding="utf-8") as file:
                spec = yaml.safe_load(file)

        elif file_path.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as file:
                spec = json.load(file)

        else:
            raise ValueError("Only .yaml, .yml and .json files are supported.")

        return self._extract_chunks(spec)

    def _extract_chunks(self, spec: dict) -> list[dict]:

        chunks = []

        paths = spec.get("paths", {})
        components = spec.get("components", {})

        # -----------------------------
        # API Endpoints
        # -----------------------------
        for endpoint, methods in paths.items():

            for method, details in methods.items():

                if method.startswith("x-"):
                    continue

                chunk = {
                    "type": "endpoint",
                    "endpoint": endpoint,
                    "method": method.upper(),
                    "summary": details.get("summary", ""),
                    "description": details.get("description", ""),
                    "parameters": details.get("parameters", []),
                    "request_body": details.get("requestBody", {}),
                    "responses": details.get("responses", {}),
                    "security": details.get("security", [])
                }

                chunks.append(chunk)

        # -----------------------------
        # Security Schemes
        # -----------------------------
        security = components.get("securitySchemes", {})

        for name, value in security.items():

            chunks.append({
                "type": "security",
                "name": name,
                "content": value
            })

        # -----------------------------
        # Schemas
        # -----------------------------
        schemas = components.get("schemas", {})

        for name, value in schemas.items():

            chunks.append({
                "type": "schema",
                "name": name,
                "content": value
            })

        return chunks