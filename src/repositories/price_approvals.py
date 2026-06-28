from sqlalchemy.orm import Session
from db.models import Item, Offer, OfferItem
from repositories.base_repository import BaseRepository


class RepositoryPriceApprovals(BaseRepository[OfferItem]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, OfferItem)

    def get_approved_offer_items_with_prices_by_component(self, component: str) -> list[OfferItem]:
        return (
            self.db.query(OfferItem)
            .join(Offer)
            .join(Item)
            .filter(Offer.component == component)
            .filter(OfferItem.approved.is_(True))
            .filter(OfferItem.unit_price.isnot(None))
            .all()
        )

    def get_offer_items_by_component(self, component: str) -> list[OfferItem]:
        return (
            self.db.query(OfferItem)
            .join(Offer)
            .filter(Offer.component == component)
            .order_by(Offer.name, OfferItem.id)
            .all()
        )

    def get_offer_item_by_id(self, offer_item_id: int) -> OfferItem | None:
        return self.db.query(OfferItem).filter(OfferItem.id == offer_item_id).first()

    def get_offer_item_by_id_for_component(self, offer_item_id: int, component: str) -> OfferItem | None:
        return (
            self.db.query(OfferItem)
            .join(Offer)
            .filter(OfferItem.id == offer_item_id)
            .filter(Offer.component == component)
            .first()
        )

    def delete_offer_item_by_id_for_component(self, offer_item_id: int, component: str) -> bool:
        offer_item = self.get_offer_item_by_id_for_component(offer_item_id, component)
        if offer_item is None:
            return False
        self.db.delete(offer_item)
        return True

    def set_offer_items_approved_by_ids_for_component(
        self,
        offer_item_ids: list[int],
        component: str,
        approved: bool,
    ) -> int:
        if not offer_item_ids:
            return 0
        matching_offer_item_ids = [
            row.id
            for row in (
                self.db.query(OfferItem.id)
                .join(Offer)
                .filter(Offer.component == component)
                .filter(OfferItem.id.in_(offer_item_ids))
                .all()
            )
        ]
        if not matching_offer_item_ids:
            return 0
        return (
            self.db.query(OfferItem)
            .filter(OfferItem.id.in_(matching_offer_item_ids))
            .update({OfferItem.approved: approved}, synchronize_session=False)
        )
