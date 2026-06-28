import config
from constants import EMBEDDING_MODEL_OPTIONS, PRICE_IMPUTATION_MODEL_OPTIONS
from schemas import AppSettingsValues


def resolve_allowed_model_name(
    stored_model_name: str,
    allowed_model_names: tuple[str, ...],
    default_model_name: str,
) -> str:
    if stored_model_name in allowed_model_names:
        return stored_model_name
    return default_model_name


def build_default_settings_values() -> AppSettingsValues:
    return AppSettingsValues(
        embedding_model=config.EMBEDDING_MODEL,
        price_imputation_model=config.PRICE_IMPUTATION_MODEL,
        preferred_websites=config.PREFERRED_WEBSITES,
        similarity_threshold=config.SIMILARITY_THRESHOLD,
        item_similarity_threshold_pricing=config.ITEM_SIMILARITY_THRESHOLD_PRICING,
        pricing_similarity_threshold=config.PRICING_SIMILARITY_THRESHOLD,
        sheet_similarity_threshold=config.SHEET_SIMILARITY_THRESHOLD,
        auto_approve_prices=config.AUTO_APPROVE_PRICES,
        merge_export_when_unit_matches=config.MERGE_EXPORT_WHEN_UNIT_MATCHES,
        price_approvals_page_size=config.PRICE_APPROVALS_PAGE_SIZE,
    )


def build_settings_values_from_stored(stored_values: dict[str, str]) -> AppSettingsValues:
    default_values = build_default_settings_values()
    stored_embedding_model = stored_values.get("embedding_model", default_values.embedding_model)
    stored_price_imputation_model = stored_values.get(
        "price_imputation_model",
        default_values.price_imputation_model,
    )
    return AppSettingsValues(
        embedding_model=resolve_allowed_model_name(
            stored_embedding_model,
            EMBEDDING_MODEL_OPTIONS,
            default_values.embedding_model,
        ),
        price_imputation_model=resolve_allowed_model_name(
            stored_price_imputation_model,
            PRICE_IMPUTATION_MODEL_OPTIONS,
            default_values.price_imputation_model,
        ),
        preferred_websites=stored_values.get(
            "preferred_websites",
            default_values.preferred_websites,
        ),
        similarity_threshold=float(
            stored_values.get("similarity_threshold", default_values.similarity_threshold)
        ),
        item_similarity_threshold_pricing=float(
            stored_values.get(
                "item_similarity_threshold_pricing",
                default_values.item_similarity_threshold_pricing,
            )
        ),
        pricing_similarity_threshold=int(
            stored_values.get(
                "pricing_similarity_threshold",
                default_values.pricing_similarity_threshold,
            )
        ),
        sheet_similarity_threshold=float(
            stored_values.get("sheet_similarity_threshold", default_values.sheet_similarity_threshold)
        ),
        auto_approve_prices=(
            stored_values.get("auto_approve_prices", str(default_values.auto_approve_prices)).lower()
            == "true"
        ),
        merge_export_when_unit_matches=(
            stored_values.get(
                "merge_export_when_unit_matches",
                str(default_values.merge_export_when_unit_matches),
            ).lower()
            == "true"
        ),
        price_approvals_page_size=int(
            stored_values.get(
                "price_approvals_page_size",
                default_values.price_approvals_page_size,
            )
        ),
    )
