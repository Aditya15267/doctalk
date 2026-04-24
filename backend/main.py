from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.database import init_db
from routes.upload import router as upload_router
from routes.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(upload_router)
app.include_router(chat_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
