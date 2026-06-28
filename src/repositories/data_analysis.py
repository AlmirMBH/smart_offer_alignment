from sqlalchemy.orm import Session
from db.models import Item, Offer, OfferItem
from repositories.base_repository import BaseRepository


class RepositoryDataAnalysis(BaseRepository[OfferItem]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, OfferItem)

    def get_offer_item_rows_by_component(self, component: str) -> list[dict[str, str | float | None]]:
        query_rows = (
            self.db.query(
                Offer.name,
                OfferItem.source_sheet,
                Item.embed_text,
                OfferItem.unit,
                OfferItem.quantity,
                OfferItem.unit_price,
                OfferItem.total_price,
            )
            .join(Offer, Offer.id == OfferItem.offer_id)
            .join(Item, Item.id == OfferItem.item_id)
            .filter(Offer.component == component)
            .order_by(Offer.name, OfferItem.id)
            .all()
        )
        return [
            {
                "offer_file": offer_name,
                "source_sheet": source_sheet,
                "embed_text": embed_text,
                "unit": unit,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": total_price,
            }
            for offer_name, source_sheet, embed_text, unit, quantity, unit_price, total_price in query_rows
        ]
