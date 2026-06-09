from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from config import DATABASE_ENGINE, DATABASE_URL


def create_database_engine(database_url: str, database_engine: str) -> Engine:
    connect_args: dict[str, object] = {}
    if database_engine == "sqlite":
        connect_args["check_same_thread"] = False
    return create_engine(database_url, connect_args=connect_args)


engine = create_database_engine(DATABASE_URL, DATABASE_ENGINE)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
