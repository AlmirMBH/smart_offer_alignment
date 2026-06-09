from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from constants import UPLOAD_DIR
from db.session import get_db
from schemas import UploadOfferResponse
from services.upload_offer import ServiceUploadOffer

router = APIRouter()


@router.post("/upload")
def route_upload_offer(
    file: UploadFile = File(...),
    component: str = Form(...),
    db: Session = Depends(get_db),
) -> UploadOfferResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    offer_filename = file.filename
    upload_path = UPLOAD_DIR / offer_filename
    upload_path.write_bytes(file.file.read())

    service_upload_offer = ServiceUploadOffer(db)
    offer, detection = service_upload_offer.upload_offer_from_excel_file(
        upload_path, offer_filename, component
    )
    upload_path.unlink()

    if offer is None:
        raise HTTPException(status_code=400, detail=detection["message"])

    item_count = detection.get("item_count", 0)
    sheets = detection.get("sheets", [])
    return {
        "offer_id": offer.id,
        "offer_name": offer.name,
        "component": offer.component,
        "item_count": item_count,
        "sheets": sheets,
    }
