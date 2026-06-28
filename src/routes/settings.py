from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from constants import EMBEDDING_MODEL_OPTIONS, PRICE_IMPUTATION_MODEL_OPTIONS
from db.session import get_db
from schemas import AppSettingsValues, SettingsGetResponse
from services.settings import ServiceSettings

router = APIRouter()


@router.get("/settings")
def route_get_settings(db: Session = Depends(get_db)) -> SettingsGetResponse:
    service_settings = ServiceSettings(db)
    settings_values = service_settings.get_settings_values()
    return SettingsGetResponse(
        **settings_values.model_dump(),
        embedding_model_options=list(EMBEDDING_MODEL_OPTIONS),
        price_imputation_model_options=list(PRICE_IMPUTATION_MODEL_OPTIONS),
    )


@router.put("/settings")
def route_update_settings(
    settings_values: AppSettingsValues,
    db: Session = Depends(get_db),
) -> AppSettingsValues:
    service_settings = ServiceSettings(db)
    return service_settings.save_settings_values(settings_values)
