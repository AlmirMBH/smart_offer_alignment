from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from schemas import OfferListItem
from services.list_offers import ServiceListOffers

router = APIRouter()


@router.get("/offers")
def route_list_offers(component: str, db: Session = Depends(get_db)) -> list[OfferListItem]:
    service_list_offers = ServiceListOffers(db)
    return service_list_offers.list_offers_by_component(component)
