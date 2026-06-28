from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from schemas import (
    BulkOfferItemsApprovalRequest,
    BulkOfferItemsApprovalResponse,
    OfferItemActionResponse,
    OfferItemDeleteResponse,
    OfferItemUpdateRequest,
    OfferItemUpdateResponse,
    PriceApprovalsResponse,
)
from services.price_approvals import ServicePriceApprovals

router = APIRouter()


@router.get("/price-approvals")
def route_list_price_approvals(
    component: str,
    db: Session = Depends(get_db),
) -> PriceApprovalsResponse:
    service_price_approvals = ServicePriceApprovals(db)
    return service_price_approvals.list_price_approval_rows_by_component(component)


@router.post("/offer-items/{offer_item_id}/approve")
def route_approve_offer_item(
    offer_item_id: int,
    db: Session = Depends(get_db),
) -> OfferItemActionResponse:
    service_price_approvals = ServicePriceApprovals(db)
    result = service_price_approvals.set_offer_item_approved(offer_item_id, True)
    if result is None:
        raise HTTPException(status_code=404, detail="Offer item not found.")
    return result


@router.post("/offer-items/{offer_item_id}/disapprove")
def route_disapprove_offer_item(
    offer_item_id: int,
    db: Session = Depends(get_db),
) -> OfferItemActionResponse:
    service_price_approvals = ServicePriceApprovals(db)
    result = service_price_approvals.set_offer_item_approved(offer_item_id, False)
    if result is None:
        raise HTTPException(status_code=404, detail="Offer item not found.")
    return result


@router.post("/offer-items/bulk-approval")
def route_bulk_set_offer_items_approved(
    component: str,
    bulk_request: BulkOfferItemsApprovalRequest,
    db: Session = Depends(get_db),
) -> BulkOfferItemsApprovalResponse:
    service_price_approvals = ServicePriceApprovals(db)
    return service_price_approvals.set_offer_items_approved_bulk(
        component,
        bulk_request.offer_item_ids,
        bulk_request.approved,
    )


@router.patch("/offer-items/{offer_item_id}")
def route_update_offer_item(
    offer_item_id: int,
    component: str,
    update_request: OfferItemUpdateRequest,
    db: Session = Depends(get_db),
) -> OfferItemUpdateResponse:
    service_price_approvals = ServicePriceApprovals(db)
    result = service_price_approvals.update_offer_item(component, offer_item_id, update_request)
    if result is None:
        raise HTTPException(status_code=404, detail="Offer item not found.")
    return result


@router.delete("/offer-items/{offer_item_id}")
def route_delete_offer_item(
    offer_item_id: int,
    component: str,
    db: Session = Depends(get_db),
) -> OfferItemDeleteResponse:
    service_price_approvals = ServicePriceApprovals(db)
    result = service_price_approvals.delete_offer_item(component, offer_item_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Offer item not found.")
    return result
