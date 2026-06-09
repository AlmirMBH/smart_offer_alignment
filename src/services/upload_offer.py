from pathlib import Path
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from config import SIMILARITY_THRESHOLD
from db.models import Item, Offer
from repositories.upload_offer import RepositoryUploadOffer
from schemas import DetectionResult, ItemDict, OfferDict, ParsedItemDict, VectorArray
from utils.embed_items import cosine_similarity, embed_items
from utils.extract_offer import extract_offer_items_from_excel_file


class ServiceUploadOffer:
    repository_upload_offer: RepositoryUploadOffer

    def __init__(self, db: Session) -> None:
        self.repository_upload_offer = RepositoryUploadOffer(db)

    def get_offer_items_dataframe_by_component(self, component: str) -> pd.DataFrame:
        return self.repository_upload_offer.get_offer_items_dataframe_by_component(component)

    def get_offers_with_embeddings_by_component(self, component: str) -> list[OfferDict]:
        offers: list[OfferDict] = []
        for offer in self.repository_upload_offer.get_offers_by_component_ordered_by_name(component):
            items: list[ItemDict] = []
            vectors: list[VectorArray] = []
            for offer_item in offer.offer_items:
                item = offer_item.item
                items.append({
                    "source_sheet": offer_item.source_sheet,
                    "parent_description": "",
                    "child_description": "",
                    "unit": offer_item.unit,
                    "quantity": offer_item.quantity,
                    "unit_price": offer_item.unit_price,
                    "total_price": offer_item.total_price,
                    "component": component,
                    "embed_text": item.embed_text,
                })
                vectors.append(np.array(item.embedding, dtype=np.float64))
            if items:
                offers.append({
                    "name": offer.name,
                    "items": items,
                    "vectors": np.array(vectors),
                })
        return offers

    def find_existing_item_by_embedding_similarity(
        self,
        existing_items: list[Item],
        item_vector: VectorArray,
        component: str,
    ) -> Item | None:
        best_item = None
        best_similarity = -1.0

        for existing_item in existing_items:
            if existing_item.component != component:
                continue
            existing_vector = np.array(existing_item.embedding)
            similarity = cosine_similarity(item_vector, existing_vector)
            if similarity > best_similarity:
                best_similarity = similarity
                best_item = existing_item
        if best_item is not None and best_similarity >= SIMILARITY_THRESHOLD:
            return best_item
        return None

    def upload_offer_from_excel_file(
        self,
        file_path: Path | str,
        offer_name: str,
        component: str,
    ) -> tuple[Offer | None, DetectionResult]:
        items, detection, _ = extract_offer_items_from_excel_file(file_path, component=component)
        if detection["status"] != "ok":
            return None, detection

        items, vectors = embed_items(items)
        repository = self.repository_upload_offer
        existing_items = repository.get_items_by_component(component)
        offer = repository.create_offer(offer_name, component)

        for item, item_vector in zip(items, vectors):
            matched_item = self.find_existing_item_by_embedding_similarity(
                existing_items, item_vector, component
            )
            if matched_item is None:
                matched_item = repository.create_item(
                    component=component,
                    embed_text=item["embed_text"],
                    embedding=item_vector.tolist(),
                )
                existing_items.append(matched_item)

            repository.create_offer_item(
                offer_id=offer.id,
                item_id=matched_item.id,
                source_sheet=item["source_sheet"],
                unit=item["unit"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                total_price=item["total_price"],
            )

        repository.commit_changes()
        detection["item_count"] = len(items)
        return offer, detection
