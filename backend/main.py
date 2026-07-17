from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from games.synonym_chain.router import router as synonym_chain_router
from games.explorer.router import router as explorer_router

from contextlib import asynccontextmanager

from driver import driver
from wordnet_service import ensure_index


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_index()
    yield


app = FastAPI(title="Syonym API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://synonymism.samwiley-stuff.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(synonym_chain_router)
app.include_router(explorer_router)


@app.get("/health")
def health():
    with driver.session() as session:
        result = session.run("RETURN 1")
        return {"status": "ok", "result": result.single()[0]}
