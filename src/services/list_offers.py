from sqlalchemy.orm import Session
from repositories.list_offers import RepositoryListOffers
from schemas import OfferListItem


class ServiceListOffers:
    repository_list_offers: RepositoryListOffers

    def __init__(self, db: Session) -> None:
        self.repository_list_offers = RepositoryListOffers(db)

    def list_offers_by_component(self, component: str) -> list[OfferListItem]:
        offers = self.repository_list_offers.get_offers_by_component_ordered_by_name(component)
        return [
            {"id": offer.id, "name": offer.name, "uploaded_at": offer.uploaded_at.isoformat()}
            for offer in offers
        ]
