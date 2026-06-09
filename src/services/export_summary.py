from pathlib import Path
from sqlalchemy.orm import Session
from repositories.export_summary import RepositoryExportSummary
from schemas import TemplateRow
from services.list_offers import ServiceListOffers
from utils.export_summary import write_summary_csv


class ServiceExportSummary:
    repository_export_summary: RepositoryExportSummary
    service_list_offers: ServiceListOffers

    def __init__(self, db: Session) -> None:
        self.repository_export_summary = RepositoryExportSummary(db)
        self.service_list_offers = ServiceListOffers(db)

    def get_offer_names_by_component(self, component: str) -> list[str]:
        offers = self.service_list_offers.list_offers_by_component(component)
        return [offer["name"] for offer in offers]

    def build_template_rows_by_component(self, component: str) -> list[TemplateRow]:
        repository = self.repository_export_summary
        items = repository.get_items_by_component(component)
        template_rows: list[TemplateRow] = []

        for item in items:
            offer_items = repository.get_offer_items_by_item_id_and_component(item.id, component)
            offers_data: TemplateRow["offers"] = {}
            for offer_item in offer_items:
                offers_data[offer_item.offer.name] = {
                    "unit": offer_item.unit,
                    "quantity": offer_item.quantity,
                    "unit_price": offer_item.unit_price,
                    "total_price": offer_item.total_price,
                    "source_sheet": offer_item.source_sheet,
                }
            template_rows.append({
                "embed_text": item.embed_text,
                "component": item.component,
                "offers": offers_data,
            })

        return template_rows

    def export_summary_csv_by_component(self, component: str, output_dir: Path) -> Path:
        offer_names = self.get_offer_names_by_component(component)
        template_rows = self.build_template_rows_by_component(component)
        return write_summary_csv(template_rows, offer_names, output_dir=output_dir)
