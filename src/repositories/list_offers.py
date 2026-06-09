from sqlalchemy.orm import Session
from db.models import Offer
from repositories.base_repository import BaseRepository


class RepositoryListOffers(BaseRepository[Offer]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Offer)

    def get_offers_by_component_ordered_by_name(self, component: str) -> list[Offer]:
        return (
            self.db.query(Offer)
            .filter(Offer.component == component)
            .order_by(Offer.name)
            .all()
        )
