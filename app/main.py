from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.projects import router as projects_router
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TrackMyRepo API",
    description=(
        "API para acompanhamento de "
        "repositórios públicos do GitHub."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    tags=["Sistema"],
    summary="Verifica se a API está funcionando",
)
def health_check():
    return {
        "status": "ok",
        "mensagem": "TrackMyRepo API funcionando.",
    }


app.include_router(projects_router)