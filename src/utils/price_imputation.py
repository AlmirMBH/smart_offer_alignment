from schemas import AppSettingsValues


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
