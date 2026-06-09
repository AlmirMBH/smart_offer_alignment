from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from schemas import DataAnalysisResponse
from services.upload_offer import ServiceUploadOffer
from utils.eda import run_data_analysis_from_dataframe

router = APIRouter()


@router.get("/data-analysis")
def route_data_analysis(component: str, db: Session = Depends(get_db)) -> DataAnalysisResponse:
    service_upload_offer = ServiceUploadOffer(db)
    items_dataframe = service_upload_offer.get_offer_items_dataframe_by_component(component)
    if len(items_dataframe) == 0:
        raise HTTPException(status_code=404, detail="No offers found for this component.")
    return run_data_analysis_from_dataframe(items_dataframe, component)
