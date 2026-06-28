from config import SIMILARITY_THRESHOLD
from schemas import ItemDict, OfferDict, OfferFieldsDict, TemplateRow, VectorArray
from utils.cosine_similarity import find_best_cosine_match


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
    return find_best_cosine_match(
        item_vector,
        template_embeddings,
        should_compare=lambda index: template_rows[index]["component"] == component,
    )


def match_offers_by_embedding_similarity(
    offers: list[OfferDict],
    similarity_threshold: float = SIMILARITY_THRESHOLD,
    merge_export_when_unit_matches: bool = False,
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
            can_merge = match_index >= 0 and best_similarity >= similarity_threshold
            if can_merge and offer_name in template_rows[match_index]["offers"]:
                can_merge = False
            if can_merge and merge_export_when_unit_matches:
                template_unit = next(iter(template_rows[match_index]["offers"].values()))["unit"].strip()
                can_merge = item["unit"].strip() == template_unit
            if can_merge:
                template_row = template_rows[match_index]
                template_row["offers"][offer_name] = build_offer_fields_from_item(item)
                template_row["embed_text"] = template_row["embed_text"] + " || " + item["embed_text"]
            else:
                template_rows.append({
                    "embed_text": item["embed_text"],
                    "component": item["component"],
                    "offers": {offer_name: build_offer_fields_from_item(item)},
                })
                template_embeddings.append(item_vector)

    return template_rows
