from fastapi import FastAPI
from constants import OUTPUT_DIR, UPLOAD_DIR
from db.models import Base
from db.session import engine
from routes import data_analysis, export_summary, home, list_offers, upload_offer, validation
from utils.embed_items import get_embedding_model


app = FastAPI()


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    get_embedding_model()


app.include_router(home.router)
app.include_router(upload_offer.router)
app.include_router(list_offers.router)
app.include_router(export_summary.router)
app.include_router(data_analysis.router)
app.include_router(validation.router)
