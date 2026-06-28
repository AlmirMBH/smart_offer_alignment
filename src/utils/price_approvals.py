from schemas import PriceApprovalRow


def build_price_approval_row(
    offer_item_id: int,
    offer_name: str,
    embed_text: str,
    unit: str,
    quantity: float,
    unit_price: float | None,
    total_price: float | None,
    source_sheet: str,
    approved: bool,
    auto_approved: bool,
) -> PriceApprovalRow:
    return PriceApprovalRow(
        offer_item_id=offer_item_id,
        offer_name=offer_name,
        embed_text=embed_text,
        unit=unit,
        quantity=quantity,
        unit_price=unit_price,
        total_price=total_price,
        source_sheet=source_sheet,
        approved=approved,
        auto_approved=auto_approved,
    )
