from pathlib import Path
import numpy as np
from sqlalchemy.orm import Session
from db.models import Offer
from repositories.export_summary import RepositoryExportSummary
from repositories.settings import RepositorySettings
from schemas import ItemDict, OfferDict, TemplateRow, VectorArray
from utils.app_settings import build_settings_values_from_stored
from utils.cosine_similarity import to_float_vector
from utils.export_summary import write_summary_csv
from utils.match_offers import match_offers_by_embedding_similarity


class ServiceExportSummary:
    repository_export_summary: RepositoryExportSummary
    repository_settings: RepositorySettings

    def __init__(self, db: Session) -> None:
        self.repository_export_summary = RepositoryExportSummary(db)
        self.repository_settings = RepositorySettings(db)

    def get_offer_names_by_component(self, component: str) -> list[str]:
        offers = self.repository_export_summary.get_offers_by_component_ordered_by_uploaded_at(component)
        return [offer.name for offer in offers]

    def build_template_rows_by_component(self, component: str) -> list[TemplateRow]:
        settings_values = build_settings_values_from_stored(
            self.repository_settings.get_all_setting_values()
        )
        offers = self.repository_export_summary.get_offers_with_items_by_component_ordered_by_uploaded_at(
            component
        )
        offer_dicts = self.build_offer_dicts_from_offers(offers, component)
        return match_offers_by_embedding_similarity(
            offer_dicts,
            similarity_threshold=settings_values.similarity_threshold,
            merge_export_when_unit_matches=settings_values.merge_export_when_unit_matches,
        )

    def export_summary_csv_by_component(self, component: str, output_dir: Path) -> Path:
        offer_names = self.get_offer_names_by_component(component)
        template_rows = self.build_template_rows_by_component(component)
        return write_summary_csv(template_rows, offer_names, output_dir=output_dir)

    def build_offer_dicts_from_offers(self, offers: list[Offer], component: str) -> list[OfferDict]:
        offer_dicts: list[OfferDict] = []
        for offer in offers:
            items: list[ItemDict] = []
            vectors: list[VectorArray] = []
            for offer_item in offer.offer_items:
                item = offer_item.item
                unit_price = offer_item.unit_price if offer_item.approved else None
                total_price = offer_item.total_price if offer_item.approved else None
                items.append({
                    "source_sheet": offer_item.source_sheet,
                    "parent_description": "",
                    "child_description": "",
                    "unit": offer_item.unit,
                    "quantity": offer_item.quantity,
                    "unit_price": unit_price,
                    "total_price": total_price,
                    "component": component,
                    "embed_text": item.embed_text,
                })
                vectors.append(to_float_vector(item.embedding))
            if items:
                offer_dicts.append({
                    "name": offer.name,
                    "items": items,
                    "vectors": np.array(vectors),
                })
        return offer_dicts
