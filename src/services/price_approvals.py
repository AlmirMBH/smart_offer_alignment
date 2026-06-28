from sqlalchemy.orm import Session
from repositories.price_approvals import RepositoryPriceApprovals
from schemas import (
    BulkOfferItemsApprovalResponse,
    OfferItemActionResponse,
    OfferItemDeleteResponse,
    OfferItemUpdateRequest,
    OfferItemUpdateResponse,
    PriceApprovalsResponse,
)
from utils.price_approvals import build_price_approval_row


class ServicePriceApprovals:
    repository_price_approvals: RepositoryPriceApprovals

    def __init__(self, db: Session) -> None:
        self.repository_price_approvals = RepositoryPriceApprovals(db)

    def list_price_approval_rows_by_component(self, component: str) -> PriceApprovalsResponse:
        offer_items = self.repository_price_approvals.get_offer_items_by_component(component)
        rows = [
            build_price_approval_row(
                offer_item_id=offer_item.id,
                offer_name=offer_item.offer.name,
                embed_text=offer_item.item.embed_text,
                unit=offer_item.unit,
                quantity=offer_item.quantity,
                unit_price=offer_item.unit_price,
                total_price=offer_item.total_price,
                source_sheet=offer_item.source_sheet,
                approved=offer_item.approved,
                auto_approved=offer_item.auto_approved,
            )
            for offer_item in offer_items
        ]
        return PriceApprovalsResponse(rows=rows)

    def set_offer_item_approved(self, offer_item_id: int, approved: bool) -> OfferItemActionResponse | None:
        offer_item = self.repository_price_approvals.get_offer_item_by_id(offer_item_id)
        if offer_item is None:
            return None
        offer_item.approved = approved
        self.repository_price_approvals.commit_changes()
        return OfferItemActionResponse(offer_item_id=offer_item.id, approved=offer_item.approved)

    def set_offer_items_approved_bulk(
        self,
        component: str,
        offer_item_ids: list[int],
        approved: bool,
    ) -> BulkOfferItemsApprovalResponse:
        updated_count = self.repository_price_approvals.set_offer_items_approved_by_ids_for_component(
            offer_item_ids,
            component,
            approved,
        )
        self.repository_price_approvals.commit_changes()
        return BulkOfferItemsApprovalResponse(updated_count=updated_count)

    def update_offer_item(
        self,
        component: str,
        offer_item_id: int,
        update_request: OfferItemUpdateRequest,
    ) -> OfferItemUpdateResponse | None:
        offer_item = self.repository_price_approvals.get_offer_item_by_id_for_component(
            offer_item_id,
            component,
        )
        if offer_item is None:
            return None
        offer_item.offer.name = update_request.offer_name
        offer_item.item.embed_text = update_request.embed_text
        offer_item.unit = update_request.unit
        offer_item.quantity = update_request.quantity
        offer_item.unit_price = update_request.unit_price
        offer_item.total_price = update_request.total_price
        offer_item.approved = update_request.approved
        self.repository_price_approvals.commit_changes()
        return OfferItemUpdateResponse(
            **build_price_approval_row(
                offer_item_id=offer_item.id,
                offer_name=offer_item.offer.name,
                embed_text=offer_item.item.embed_text,
                unit=offer_item.unit,
                quantity=offer_item.quantity,
                unit_price=offer_item.unit_price,
                total_price=offer_item.total_price,
                source_sheet=offer_item.source_sheet,
                approved=offer_item.approved,
                auto_approved=offer_item.auto_approved,
            ).model_dump()
        )

    def delete_offer_item(self, component: str, offer_item_id: int) -> OfferItemDeleteResponse | None:
        deleted = self.repository_price_approvals.delete_offer_item_by_id_for_component(
            offer_item_id,
            component,
        )
        if not deleted:
            return None
        self.repository_price_approvals.commit_changes()
        return OfferItemDeleteResponse(offer_item_id=offer_item_id)
