from typing import Generic, TypeVar
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    db: Session
    model_class: type[ModelType]

    def __init__(self, db: Session, model_class: type[ModelType]) -> None:
        self.db = db
        self.model_class = model_class

    def add_entity(self, entity: ModelType) -> ModelType:
        self.db.add(entity)
        return entity

    def flush_changes(self) -> None:
        self.db.flush()

    def commit_changes(self) -> None:
        self.db.commit()
