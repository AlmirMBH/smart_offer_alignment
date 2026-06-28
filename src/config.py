import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv
from constants import DEFAULT_PREFERRED_WEBSITES, PROJECT_ROOT

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_ENGINE = os.getenv("DATABASE_ENGINE", "sqlite").lower()
SQLITE_DATABASE_PATH = os.getenv("SQLITE_DATABASE_PATH", "./app.db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "")
POSTGRES_USER = os.getenv("POSTGRES_USER", "")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
PRICE_IMPUTATION_MODEL = os.getenv("PRICE_IMPUTATION_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
PREFERRED_WEBSITES = os.getenv("PREFERRED_WEBSITES", DEFAULT_PREFERRED_WEBSITES)
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
ITEM_SIMILARITY_THRESHOLD_PRICING = float(os.getenv("ITEM_SIMILARITY_THRESHOLD_PRICING", "0.85"))
PRICING_SIMILARITY_THRESHOLD = int(os.getenv("PRICING_SIMILARITY_THRESHOLD", "20"))
SHEET_SIMILARITY_THRESHOLD = float(os.getenv("SHEET_SIMILARITY_THRESHOLD", "0.75"))
AUTO_APPROVE_PRICES = os.getenv("AUTO_APPROVE_PRICES", "false").lower() == "true"
MERGE_EXPORT_WHEN_UNIT_MATCHES = os.getenv("MERGE_EXPORT_WHEN_UNIT_MATCHES", "false").lower() == "true"
PRICE_APPROVALS_PAGE_SIZE = int(os.getenv("PRICE_APPROVALS_PAGE_SIZE", "6"))


def build_sqlite_database_path() -> str:
    sqlite_path = Path(SQLITE_DATABASE_PATH)
    if not sqlite_path.is_absolute():
        sqlite_path = PROJECT_ROOT / sqlite_path
    return str(sqlite_path)


def build_database_url() -> str:
    if DATABASE_ENGINE == "sqlite":
        return f"sqlite:///{build_sqlite_database_path()}"

    if DATABASE_ENGINE == "postgresql":
        missing_variables = [
            variable_name
            for variable_name, variable_value in {
                "POSTGRES_HOST": POSTGRES_HOST,
                "POSTGRES_DB": POSTGRES_DB,
                "POSTGRES_USER": POSTGRES_USER,
                "POSTGRES_PASSWORD": POSTGRES_PASSWORD,
            }.items()
            if not variable_value
        ]
        if missing_variables:
            missing_list = ", ".join(missing_variables)
            raise ValueError(f"Missing required PostgreSQL environment variables: {missing_list}")

        encoded_password = quote_plus(POSTGRES_PASSWORD)
        return (
            f"postgresql+psycopg2://{POSTGRES_USER}:{encoded_password}"
            f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )

    raise ValueError(f"Unsupported DATABASE_ENGINE: {DATABASE_ENGINE}")


DATABASE_URL = build_database_url()
