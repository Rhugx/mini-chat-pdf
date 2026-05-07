from fastapi import FastAPI
from backend.app.api.upload import router as upload_router
from backend.app.api.ask import router as ask_router

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Project running + DB ready"}

# 👇 THIS LINE IS IMPORTANT
app.include_router(upload_router)
app.include_router(ask_router)