from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from schemas import ValidationResponse
from services.upload_offer import ServiceUploadOffer
from utils.validate_threshold import run_validation_from_offers

router = APIRouter()


@router.get("/validation")
def route_validation(component: str, db: Session = Depends(get_db)) -> ValidationResponse:
    service_upload_offer = ServiceUploadOffer(db)
    offers = service_upload_offer.get_offers_with_embeddings_by_component(component)
    if len(offers) < 2:
        raise HTTPException(
            status_code=404,
            detail="Need at least 2 offers with items for validation.",
        )
    return run_validation_from_offers(offers)
