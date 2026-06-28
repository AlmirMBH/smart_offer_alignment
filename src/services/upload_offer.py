from pathlib import Path
from sqlalchemy.orm import Session
from constants import UPLOAD_DIR
from db.models import Offer, OfferItem
from clients.embedding import encode_texts
from clients.web import fetch_page_text
from repositories.price_approvals import RepositoryPriceApprovals
from repositories.settings import RepositorySettings
from repositories.upload_offer import RepositoryUploadOffer
from schemas import AppSettingsValues, DetectionResult, VectorArray
from utils.app_settings import build_settings_values_from_stored
from utils.clean_embed_text import clean_embed_text
from utils.cosine_similarity import find_best_cosine_match, to_float_vector
from utils.extract_offer import parse_offer_items_from_detection
from utils.find_component_sheets import component_label_texts, find_component_sheets
from utils.internet_price_catalog import get_price_catalog_for_websites, parse_preferred_websites
from utils.load_excel import list_workbook_sheet_names
from utils.price_imputation import (
    calculate_total_price,
    find_best_catalog_price,
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

    def upload_offer_from_upload_file(
        self,
        file_bytes: bytes,
        offer_name: str,
        component: str,
    ) -> tuple[Offer | None, DetectionResult]:
        upload_path = UPLOAD_DIR / offer_name
        upload_path.write_bytes(file_bytes)
        try:
            return self.upload_offer_from_excel_file(upload_path, offer_name, component)
        finally:
            if upload_path.exists():
                upload_path.unlink()

    def upload_offer_from_excel_file(
        self,
        file_path: Path | str,
        offer_name: str,
        component: str,
    ) -> tuple[Offer | None, DetectionResult]:
        settings_values = build_settings_values_from_stored(
            self.repository_settings.get_all_setting_values()
        )
        embedding_model_name = settings_values.embedding_model
        sheet_names = list_workbook_sheet_names(file_path)
        component_vectors = encode_texts(embedding_model_name, component_label_texts(component))
        sheet_vectors = encode_texts(embedding_model_name, sheet_names)
        detection = find_component_sheets(
            file_path,
            component,
            settings_values.sheet_similarity_threshold,
            component_vectors,
            sheet_vectors,
        )
        items, _ = parse_offer_items_from_detection(file_path, component, detection)
        if detection["status"] != "ok":
            return None, detection

        cleaned_texts = [clean_embed_text(item["embed_text"]) for item in items]
        vectors = encode_texts(embedding_model_name, cleaned_texts)
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

            imputed_unit_price = self.impute_unit_price_from_internet(
                embed_text,
                settings_values,
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
        reference_vectors = [
            to_float_vector(approved_offer_item.item.embedding)
            for approved_offer_item in approved_offer_items
        ]
        best_index, _ = find_best_cosine_match(
            item_vector,
            reference_vectors,
            should_compare=lambda index: approved_offer_items[index].id != exclude_offer_item_id,
            minimum_similarity=item_similarity_threshold_pricing,
        )
        if best_index < 0:
            return None
        return approved_offer_items[best_index].unit_price

    def impute_unit_price_from_internet(
        self,
        item_description: str,
        settings_values: AppSettingsValues,
    ) -> float | None:
        preferred_websites = parse_preferred_websites(settings_values.preferred_websites)
        if not preferred_websites:
            return None

        page_texts = [fetch_page_text(website_url) for website_url in preferred_websites]
        catalog = get_price_catalog_for_websites(preferred_websites, page_texts)
        if not catalog:
            return None

        price_imputation_model_name = settings_values.price_imputation_model
        item_vector = encode_texts(price_imputation_model_name, [item_description])[0]
        catalog_descriptions = [catalog_row[0] for catalog_row in catalog]
        catalog_vectors = encode_texts(price_imputation_model_name, catalog_descriptions)
        return find_best_catalog_price(catalog, item_vector, catalog_vectors)
