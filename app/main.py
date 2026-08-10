from fastapi import FastAPI
from app.api.routes import router
from app.database.db import Base, engine
from app.database import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="APIMind AI")

app.include_router(router)