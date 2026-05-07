from fastapi import FastAPI

from app.api.upload import router as upload_router
from app.api.ask import router as ask_router

from app.core.database import Base, engine
from app.models.vector_store import Document

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Register routes
app.include_router(upload_router)
app.include_router(ask_router)