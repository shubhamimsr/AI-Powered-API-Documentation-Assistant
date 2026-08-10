import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# Groq Configuration
# ==========================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

BASE_URL = "https://api.groq.com/openai/v1"

MODEL_NAME = "llama-3.1-8b-instant"


# ==========================================================
# PostgreSQL Configuration
# ==========================================================

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# ==========================================================
# Retrieval Configuration
# ==========================================================

VECTOR_TOP_K = 10

RERANK_TOP_K = 3

RRF_K = 60

USE_RERANKER = True

# ==========================================================
# Query Rewriter
# ==========================================================

USE_QUERY_REWRITER = True

# --------------------------------
# Confidence Threshold
# --------------------------------

MIN_CONFIDENCE = 0.45