import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session
from db.models import Offer, OfferItem
from clients.embedding import cosine_similarity, embed_items
from clients.price_imputation import impute_unit_price
from repositories.price_approvals import RepositoryPriceApprovals
from repositories.settings import RepositorySettings
from repositories.upload_offer import RepositoryUploadOffer
from schemas import AppSettingsValues, DetectionResult, VectorArray
from utils.app_settings import build_settings_values_from_stored
from utils.extract_offer import extract_offer_items_from_excel_file
from utils.price_imputation import (
    calculate_total_price,
    price_is_missing,
    should_auto_approve_imputed_price,
)


class ServiceUploadOffer:
    repository_upload_offer: RepositoryUploadOffer
    repository_price_approvals: RepositoryPriceApprovals
    repository_settings: RepositorySettings

    def __init__(self, db: Session) -> None:
        self.repository_upload_offer = RepositoryUploadOffer(db)
        self.repository_price_approvals = RepositoryPriceApprovals(db)
        self.repository_settings = RepositorySettings(db)

    def upload_offer_from_excel_file(
        self,
        file_path: Path | str,
        offer_name: str,
        component: str,
    ) -> tuple[Offer | None, DetectionResult]:
        settings_values = build_settings_values_from_stored(
            self.repository_settings.get_all_setting_values()
        )
        items, detection, _ = extract_offer_items_from_excel_file(
            file_path,
            component=component,
            sheet_similarity_threshold=settings_values.sheet_similarity_threshold,
        )
        if detection["status"] != "ok":
            return None, detection

        items, vectors = embed_items(items)
        repository_upload_offer = self.repository_upload_offer
        offer = repository_upload_offer.create_offer(offer_name, component)
        offer_items_for_imputation: list[tuple[OfferItem, VectorArray, str]] = []

        for item, item_vector in zip(items, vectors):
            stored_item = repository_upload_offer.create_item(
                component=component,
                embed_text=item["embed_text"],
                embedding=item_vector.tolist(),
            )
            excel_price_present = not price_is_missing(item["unit_price"])
            offer_item = repository_upload_offer.create_offer_item(
                offer_id=offer.id,
                item_id=stored_item.id,
                source_sheet=item["source_sheet"],
                unit=item["unit"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                total_price=item["total_price"],
                approved=excel_price_present,
            )
            if price_is_missing(item["unit_price"]):
                offer_items_for_imputation.append((offer_item, item_vector, item["embed_text"]))

        self.impute_offer_item_prices_at_ingest(
            offer_items_for_imputation,
            component,
            settings_values,
        )
        repository_upload_offer.commit_changes()

        detection["item_count"] = len(items)
        return offer, detection

    def impute_offer_item_prices_at_ingest(
        self,
        offer_items_with_vectors: list[tuple[OfferItem, VectorArray, str]],
        component: str,
        settings_values: AppSettingsValues,
    ) -> None:
        for offer_item, item_vector, embed_text in offer_items_with_vectors:
            if not price_is_missing(offer_item.unit_price):
                offer_item.approved = True
                offer_item.auto_approved = False
                continue

            imputed_unit_price = impute_unit_price(
                embed_text,
                settings_values.price_imputation_model,
                settings_values.preferred_websites,
            )
            if imputed_unit_price is None:
                offer_item.approved = False
                offer_item.auto_approved = False
                continue

            offer_item.unit_price = imputed_unit_price
            offer_item.total_price = calculate_total_price(offer_item.quantity, imputed_unit_price)

            reference_unit_price = self.find_approved_reference_unit_price(
                item_vector,
                component,
                offer_item.id,
                settings_values.item_similarity_threshold_pricing,
            )
            if reference_unit_price is None:
                offer_item.approved = False
                offer_item.auto_approved = False
                continue

            is_auto_approved = should_auto_approve_imputed_price(
                imputed_unit_price,
                reference_unit_price,
                settings_values,
            )
            offer_item.approved = is_auto_approved
            offer_item.auto_approved = is_auto_approved

    def find_approved_reference_unit_price(
        self,
        item_vector: VectorArray,
        component: str,
        exclude_offer_item_id: int,
        item_similarity_threshold_pricing: float,
    ) -> float | None:
        approved_offer_items = (
            self.repository_price_approvals.get_approved_offer_items_with_prices_by_component(component)
        )
        best_reference_unit_price = None
        best_similarity = -1.0

        for approved_offer_item in approved_offer_items:
            if approved_offer_item.id == exclude_offer_item_id:
                continue
            reference_vector = np.array(approved_offer_item.item.embedding, dtype=np.float64)
            if reference_vector.shape != item_vector.shape:
                continue
            similarity = cosine_similarity(item_vector, reference_vector)
            if similarity >= item_similarity_threshold_pricing and similarity > best_similarity:
                best_similarity = similarity
                best_reference_unit_price = approved_offer_item.unit_price

        return best_reference_unit_price
