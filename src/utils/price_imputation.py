from constants import PRICE_IMPUTATION_MIN_CATALOG_SIMILARITY
from schemas import AppSettingsValues, VectorArray
from utils.cosine_similarity import find_best_cosine_match


def price_is_missing(unit_price: float | None) -> bool:
    return unit_price is None


def calculate_total_price(quantity: float, unit_price: float) -> float:
    return quantity * unit_price


def is_price_within_percent_range(
    imputed_unit_price: float,
    reference_unit_price: float,
    pricing_similarity_threshold_percent: int,
) -> bool:
    if reference_unit_price == 0:
        return False
    percent_difference = abs(imputed_unit_price - reference_unit_price) / reference_unit_price * 100
    return percent_difference <= pricing_similarity_threshold_percent


def should_auto_approve_imputed_price(
    imputed_unit_price: float,
    reference_unit_price: float,
    settings_values: AppSettingsValues,
) -> bool:
    if not settings_values.auto_approve_prices:
        return False
    return is_price_within_percent_range(
        imputed_unit_price,
        reference_unit_price,
        settings_values.pricing_similarity_threshold,
    )


def find_best_catalog_price(
    catalog: list[tuple[str, float]],
    item_vector: VectorArray,
    catalog_vectors: VectorArray,
) -> float | None:
    if not catalog:
        return None

    catalog_vector_list = [catalog_vectors[index] for index in range(len(catalog))]
    best_index, best_similarity = find_best_cosine_match(
        item_vector,
        catalog_vector_list,
        skip_shape_mismatch=False,
    )
    if best_index < 0 or best_similarity < PRICE_IMPUTATION_MIN_CATALOG_SIMILARITY:
        return None
    return catalog[best_index][1]
