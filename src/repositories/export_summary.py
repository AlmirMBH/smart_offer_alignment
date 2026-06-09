from sqlalchemy.orm import Session
from db.models import Item, Offer, OfferItem
from repositories.base_repository import BaseRepository


class RepositoryExportSummary(BaseRepository[Offer]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Offer)

    def get_items_by_component(self, component: str) -> list[Item]:
        return self.db.query(Item).filter(Item.component == component).all()

    def get_offer_items_by_item_id_and_component(self, item_id: int, component: str) -> list[OfferItem]:
        return (
            self.db.query(OfferItem)
            .join(Offer)
            .filter(OfferItem.item_id == item_id, Offer.component == component)
            .all()
        )
