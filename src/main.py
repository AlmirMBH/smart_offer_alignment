from fastapi import FastAPI
from constants import OUTPUT_DIR, UPLOAD_DIR
from config import EMBEDDING_MODEL
from routes import data_analysis, export_summary, home, list_offers, price_approvals, settings, upload_offer
from clients.embedding import load_embedding_model


app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    load_embedding_model(EMBEDDING_MODEL)


app.include_router(home.router)
app.include_router(upload_offer.router)
app.include_router(list_offers.router)
app.include_router(export_summary.router)
app.include_router(data_analysis.router)
app.include_router(price_approvals.router)
app.include_router(settings.router)
