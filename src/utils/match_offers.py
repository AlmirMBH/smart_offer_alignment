from config import SIMILARITY_THRESHOLD
from schemas import ItemDict, OfferDict, OfferFieldsDict, TemplateRow, VectorArray
from utils.embed_items import cosine_similarity


def build_offer_fields_from_item(item: ItemDict) -> OfferFieldsDict:
    return {
        "unit": item["unit"],
        "quantity": item["quantity"],
        "unit_price": item["unit_price"],
        "total_price": item["total_price"],
        "source_sheet": item["source_sheet"],
    }


def find_best_template_match_for_item_vector(
    item_vector: VectorArray,
    template_embeddings: list[VectorArray],
    template_rows: list[TemplateRow],
    component: str,
) -> tuple[int, float]:
    best_index = -1
    best_similarity = -1.0
    for index, template_vector in enumerate(template_embeddings):
        if template_rows[index]["component"] != component:
            continue
        similarity = cosine_similarity(item_vector, template_vector)
        if similarity > best_similarity:
            best_similarity = similarity
            best_index = index
    return best_index, best_similarity


def match_offers_by_embedding_similarity(
    offers: list[OfferDict],
    similarity_threshold: float = SIMILARITY_THRESHOLD,
) -> list[TemplateRow]:
    template_rows: list[TemplateRow] = []
    template_embeddings: list[VectorArray] = []

    for offer in offers:
        offer_name = offer["name"]
        for item_index, item in enumerate(offer["items"]):
            item_vector = offer["vectors"][item_index]
            match_index, best_similarity = find_best_template_match_for_item_vector(
                item_vector,
                template_embeddings,
                template_rows,
                item["component"],
            )
            if match_index >= 0 and best_similarity >= similarity_threshold:
                template_rows[match_index]["offers"][offer_name] = build_offer_fields_from_item(item)
            else:
                template_rows.append({
                    "embed_text": item["embed_text"],
                    "component": item["component"],
                    "offers": {offer_name: build_offer_fields_from_item(item)},
                })
                template_embeddings.append(item_vector)

    return template_rows
