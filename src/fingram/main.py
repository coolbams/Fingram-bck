from fastapi import FastAPI
from .api.document import file_router
from contextlib import asynccontextmanager

from .database.connection import init_db

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(debug = True, title="Fingram bckend server", lifespan=lifespan)

app.include_router(file_router, prefix="/upload_file")


@app.get("/health")
def health():
    """ Returns Health of the Server  """
    return{"status" : "200"}


