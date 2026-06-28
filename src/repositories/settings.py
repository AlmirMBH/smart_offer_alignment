from sqlalchemy.orm import Session
from db.models import AppSetting
from repositories.base_repository import BaseRepository


class RepositorySettings(BaseRepository[AppSetting]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, AppSetting)

    def get_setting_value(self, setting_key: str) -> str | None:
        setting_row = self.db.query(AppSetting).filter(AppSetting.key == setting_key).first()
        if setting_row is None:
            return None
        return setting_row.value

    def set_setting_value(self, setting_key: str, setting_value: str) -> None:
        setting_row = self.db.query(AppSetting).filter(AppSetting.key == setting_key).first()
        if setting_row is None:
            self.add_entity(AppSetting(key=setting_key, value=setting_value))
            return
        setting_row.value = setting_value

    def get_all_setting_values(self) -> dict[str, str]:
        setting_rows = self.db.query(AppSetting).all()
        return {setting_row.key: setting_row.value for setting_row in setting_rows}
