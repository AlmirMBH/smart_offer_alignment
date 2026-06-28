from sqlalchemy.orm import Session
from db.models import Item, Offer, OfferItem
from repositories.base_repository import BaseRepository


class RepositoryUploadOffer(BaseRepository[Offer]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Offer)

    def create_offer(self, offer_name: str, component: str) -> Offer:
        offer = Offer(name=offer_name, component=component)
        self.add_entity(offer)
        self.flush_changes()
        return offer

    def create_item(self, component: str, embed_text: str, embedding: list[float]) -> Item:
        item = Item(component=component, embed_text=embed_text, embedding=embedding)
        self.add_entity(item)
        self.flush_changes()
        return item

    def create_offer_item(
        self,
        offer_id: int,
        item_id: int,
        source_sheet: str,
        unit: str,
        quantity: float,
        unit_price: float | None,
        total_price: float | None,
        approved: bool = False,
        auto_approved: bool = False,
    ) -> OfferItem:
        offer_item = OfferItem(
            offer_id=offer_id,
            item_id=item_id,
            source_sheet=source_sheet,
            unit=unit,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            approved=approved,
            auto_approved=auto_approved,
        )
        self.add_entity(offer_item)
        self.flush_changes()
        return offer_item
