from sqlalchemy.orm import Session, joinedload
from db.models import Offer, OfferItem
from repositories.base_repository import BaseRepository


class RepositoryExportSummary(BaseRepository[Offer]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Offer)

    def get_offers_by_component_ordered_by_uploaded_at(self, component: str) -> list[Offer]:
        return (
            self.db.query(Offer)
            .filter(Offer.component == component)
            .order_by(Offer.uploaded_at, Offer.id)
            .all()
        )

    def get_offers_with_items_by_component_ordered_by_uploaded_at(self, component: str) -> list[Offer]:
        return (
            self.db.query(Offer)
            .options(joinedload(Offer.offer_items).joinedload(OfferItem.item))
            .filter(Offer.component == component)
            .order_by(Offer.uploaded_at, Offer.id)
            .all()
        )
