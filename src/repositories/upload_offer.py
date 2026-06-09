import pandas as pd
from sqlalchemy.orm import Session
from db.models import Item, Offer, OfferItem
from repositories.base_repository import BaseRepository


class RepositoryUploadOffer(BaseRepository[Offer]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Offer)

    def get_offers_by_component_ordered_by_name(self, component: str) -> list[Offer]:
        return (
            self.db.query(Offer)
            .filter(Offer.component == component)
            .order_by(Offer.name)
            .all()
        )

    def get_offer_items_dataframe_by_component(self, component: str) -> pd.DataFrame:
        rows: list[dict[str, str | float | None]] = []
        for offer in self.get_offers_by_component_ordered_by_name(component):
            for offer_item in offer.offer_items:
                rows.append({
                    "offer_file": offer.name,
                    "source_sheet": offer_item.source_sheet,
                    "embed_text": offer_item.item.embed_text,
                    "unit": offer_item.unit,
                    "quantity": offer_item.quantity,
                    "unit_price": offer_item.unit_price,
                    "total_price": offer_item.total_price,
                    "embed_text": offer_item.item.embed_text,
                })
        return pd.DataFrame(rows)

    def get_items_by_component(self, component: str) -> list[Item]:
        return self.db.query(Item).filter(Item.component == component).all()

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
    ) -> OfferItem:
        offer_item = OfferItem(
            offer_id=offer_id,
            item_id=item_id,
            source_sheet=source_sheet,
            unit=unit,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
        )
        self.add_entity(offer_item)
        return offer_item
