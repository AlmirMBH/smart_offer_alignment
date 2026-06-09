from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from constants import OUTPUT_DIR
from db.session import get_db
from services.export_summary import ServiceExportSummary


router = APIRouter()


@router.get("/summary")
def route_export_summary(component: str, db: Session = Depends(get_db)) -> FileResponse:
    service_export_summary = ServiceExportSummary(db)
    offer_names = service_export_summary.get_offer_names_by_component(component)
    if not offer_names:
        raise HTTPException(status_code=404, detail="No offers found for this component.")

    output_path = service_export_summary.export_summary_csv_by_component(component, OUTPUT_DIR)
    return FileResponse(output_path, filename=output_path.name, media_type="text/csv")
