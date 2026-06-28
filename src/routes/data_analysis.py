from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from schemas import DataAnalysisResponse
from services.data_analysis import ServiceDataAnalysis

router = APIRouter()


@router.get("/data-analysis")
def route_data_analysis(component: str, db: Session = Depends(get_db)) -> DataAnalysisResponse:
    service_data_analysis = ServiceDataAnalysis(db)
    data_analysis_response = service_data_analysis.run_data_analysis_by_component(component)
    if data_analysis_response is None:
        raise HTTPException(status_code=404, detail="No offers found for this component.")
    return data_analysis_response
