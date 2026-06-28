from sqlalchemy.orm import Session
from clients.embedding import clear_model_cache
from utils.internet_price_catalog import clear_price_catalog_cache
from repositories.settings import RepositorySettings
from schemas import AppSettingsValues
from utils.app_settings import build_settings_values_from_stored


class ServiceSettings:
    repository_settings: RepositorySettings

    def __init__(self, db: Session) -> None:
        self.repository_settings = RepositorySettings(db)

    def get_settings_values(self) -> AppSettingsValues:
        return build_settings_values_from_stored(self.repository_settings.get_all_setting_values())

    def save_settings_values(self, settings_values: AppSettingsValues) -> AppSettingsValues:
        previous_values = self.get_settings_values()
        repository = self.repository_settings
        repository.set_setting_value("embedding_model", settings_values.embedding_model)
        repository.set_setting_value("price_imputation_model", settings_values.price_imputation_model)
        repository.set_setting_value("preferred_websites", settings_values.preferred_websites)
        repository.set_setting_value("similarity_threshold", str(settings_values.similarity_threshold))
        repository.set_setting_value(
            "item_similarity_threshold_pricing",
            str(settings_values.item_similarity_threshold_pricing),
        )
        repository.set_setting_value(
            "pricing_similarity_threshold",
            str(settings_values.pricing_similarity_threshold),
        )
        repository.set_setting_value(
            "sheet_similarity_threshold",
            str(settings_values.sheet_similarity_threshold),
        )
        repository.set_setting_value(
            "auto_approve_prices",
            "true" if settings_values.auto_approve_prices else "false",
        )
        repository.set_setting_value(
            "merge_export_when_unit_matches",
            "true" if settings_values.merge_export_when_unit_matches else "false",
        )
        repository.set_setting_value(
            "price_approvals_page_size",
            str(settings_values.price_approvals_page_size),
        )
        repository.commit_changes()
        self.apply_runtime_setting_changes(previous_values, settings_values)
        return settings_values

    def apply_runtime_setting_changes(
        self,
        previous_values: AppSettingsValues,
        saved_values: AppSettingsValues,
    ) -> None:
        if saved_values.embedding_model != previous_values.embedding_model:
            clear_model_cache(previous_values.embedding_model)
            clear_model_cache(saved_values.embedding_model)
        if saved_values.price_imputation_model != previous_values.price_imputation_model:
            for model_name in {
                previous_values.price_imputation_model,
                saved_values.price_imputation_model,
            }:
                clear_model_cache(model_name)
        if saved_values.preferred_websites != previous_values.preferred_websites:
            clear_price_catalog_cache()
