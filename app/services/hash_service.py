import hashlib


class HashService:

    @staticmethod
    def calculate(file_bytes: bytes):

        return hashlib.sha256(file_bytes).hexdigest()