from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root(request: Request):
    return JSONResponse(content={"message": "Hello World!"})